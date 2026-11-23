LAB 18 — PROJECT 2 REFERENCE

Scope: prior coursework used only from Lab14, lab 15, Lab 16 and Lab 17.
No Project 1, older labs, or price datasets feed this analysis.

RUN (from the Lab 18 directory)
  uv run --with streamlit python -m streamlit run app.py --server.port 8504

FIRST LIVE DOWNLOAD
Set the SEC contact header using your real email, for example:
  $env:SEC_USER_AGENT = 'Mason Smith YOUR_REAL_EMAIL'
  uv run python buffett-sec/scripts/sec_facts.py COST --output results
  uv run python buffett-sec/scripts/sec_facts.py JPM --output results
Or enter the same contact header and download with the app.
The program deliberately rejects a missing email. Never invent an email.

THEN ASK CODEX
  Use $buffett-sec on COST with the saved SEC results in Lab 18/results.
  Read numbers.md and save a short Buffett-inspired AI memo to
  results/COST/memo.md using only printed numbers. Repeat for JPM;
  missing owner earnings must explicitly limit judgment.

The skill source is buffett-sec/SKILL.md. It is also installed in
C:/Users/mason/.codex/skills/buffett-sec for discovery in future chats.
The app supports any ticker with saved results and can download new ones.
AI judgment is written by Codex, not a formula pretending to be the model.
An existing memo is revalidated against newly downloaded data automatically.

VERIFY
  uv run python test_engine.py
  uv run --with streamlit python test_app.py
  uv run python verify.py
verification.txt reports live comparison status. known_answer.json is only
the instructor's pasted fixture. It never supplies company results.
Unexpected SEC values must be investigated, never overwritten to pass.

YOUR CLASSROOM ACTIONS
- Explain code-computable ROE vs judgment about a durable moat to your partner.
- Open Brightspace > Quizzes > Lab 18 at the assigned class time.
- Explain year_row in buffett-sec/scripts/sec_facts.py line by line without AI.
- Type 40.0% in the memo editor and inspect the warning; restore the memo.
- In a separate browser AI chat without the skill, ask the supplied question
  about Costco ROE. Record its response and compare sources and periods.
- Enter your own one-line trust decision below the memo and save it.
The partner discussion, quiz, fresh-chat comparison and your personal
decision have not been represented as completed by the AI.

STATUS
Read verification.txt for live-data status. At initial build the real SEC
contact email was pending, so no COST or JPM result/memo was fabricated.
