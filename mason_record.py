"""Verified app presentation of Mason's user-supplied locked allocation test."""
import hashlib
import json
from pathlib import Path
import numpy as np
import portfolio as p
import current_rules as rules
from data_integrity import verify


def load_record(root):
    root = Path(root)
    verify(root)
    receipt = json.loads((root/'docs/mason-locked-commit.json').read_text(encoding='utf-8'))
    for name,digest in receipt['locked_sha256'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('STOP: Mason pre-run record changed: '+name)
    spec = json.loads((root/'docs/mason-locked-input.json').read_text(encoding='utf-8'))
    for name,digest in spec['frozen_sha256'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('STOP: Mason test frozen input changed: '+name)
    post = json.loads((root/'docs/mason-locked-result-receipt.json').read_text(encoding='utf-8'))
    raw = (root/'outputs/mason-locked-result.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=post['result_sha256']:
        raise ValueError('STOP: saved Mason result differs from its recorded run hash.')
    result = json.loads(raw)
    if result['pre_run_commit']!=receipt:
        raise ValueError('STOP: result references a different pre-run commit.')
    assets,corr = p.estimate_from_csv(root/'prices.csv')
    for a in assets:
        a['reserve_eligible'] = a['name']=='SGOV'
    for key,w in [('original',spec['original_weights']),('revised',spec['revised_weights'])]:
        fresh = rules.evaluate(w,assets,corr)
        for metric in ['weights','return','volatility','reserve_weight']:
            np.testing.assert_allclose(result[key][metric],fresh[metric],atol=1e-12,rtol=0)
        if result[key]['checks']!=fresh['checks'] or result[key]['feasible']!=fresh['feasible']:
            raise ValueError('STOP: saved rule verdict differs from app calculation.')
    return result


def render(root):
    import streamlit as st
    root = Path(root)
    st.subheader("Mason's user-supplied Locked Changed-Input Record")
    st.caption('Prediction supplied by Mason, who reports AI-off preparation. Packaging, execution and arithmetic verification were AI-assisted; no independent validation is claimed.')
    try:
        result = load_record(root)
        rows=[]
        for label,key in [('Original','original'),('Revised — Mason’s change','revised')]:
            s=result[key]
            rows.append({'Allocation':label,'SGOV / VGIT / VCIT / ACWI':' / '.join(f'{w:.0%}' for w in s['weights']),
                         'Expected annual return':f"{s['return']:.4%}",'Annualized volatility':f"{s['volatility']:.4%}",
                         'SGOV reserves':f"{s['reserve_weight']:.0%}",'Numerical pilot verdict':'PASS' if s['feasible'] else 'FAIL',
                         'Failed rule':' | '.join(s['failed_rules']) or 'None'})
        st.dataframe(rows,hide_index=True,width='stretch')
        st.dataframe([{'User prediction':k.replace('_',' '),'Result':'Supported' if v else 'Not supported'} for k,v in result['prediction_outcomes'].items()],hide_index=True)
        st.write(result['decision'])
        st.caption('The app recalculates these metrics from frozen prices and verifies agreement with the saved run. Historical estimates, not realized future performance; original mandate remains partly untested, and no live capital is authorized.')
        st.markdown(f"[Pre-run GitHub commit]({result['pre_run_commit']['commit_url']})")
        st.caption('Committed: '+result['pre_run_commit']['committed_at_utc']+' | First recorded run: '+result['run_at_utc'])
        st.download_button('Download Mason submission summary',(root/'docs/mason-locked-submission.md').read_bytes(),'mason-locked-submission.md','text/markdown',key='mason-summary-'+st.session_state.get('app_section',''))
        with st.expander('Read the verbatim pre-run prediction and saved result'):
            st.markdown((root/'docs/mason-locked-prediction.md').read_text(encoding='utf-8'))
            st.json(result)
    except (ValueError,OSError,KeyError,AssertionError,TypeError) as error:
        st.error('STOP: cannot verify Mason’s locked record: '+str(error))
