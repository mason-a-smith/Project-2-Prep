# Project 2 fund vintage audit

Archived download: 2026-10-22T21:27:42.703541+00:00. Fresh audit completed: 2026-10-29T21:18:11.004642+00:00.

Same measured window: September 2021–September 2026. This compares two actual download vintages, not reconstructed September 30 availability. Yahoo has no ALFRED-style historical-vintage endpoint used here.

```text
Series  Shared month-end dates  Changed adjusted levels (> $0.000001)  Max adjusted level difference ($)  Changed monthly returns (> 0.000001)  Max return difference (percentage points) Last measured date  Archived last adjusted price  Current last adjusted price
  SGOV                      61                                     49                           0.000053                                     0                                   0.000073         2026-09-30                    100.379005                   100.379005
  VGIT                      61                                     51                           0.000027                                     0                                   0.000068         2026-09-30                     56.470997                    56.470997
  VCIT                      61                                     44                           0.000046                                     0                                   0.000099         2026-09-30                     77.969994                    77.969994
  ACWI                      61                                     22                           0.000015                                     0                                   0.000024         2026-09-30                    158.770004                   158.770004
```

Return tolerance is 0.000001 in decimal return (0.0001 percentage point); level tolerance is $0.000001 to avoid counting CSV rounding noise. Adjusted-level changes do not necessarily change returns: a common multiplicative adjustment cancels in the return ratio. A zero count across these two downloads does not prove zero revisions over the entire history.
