# Score — opus-5/run_1

Task: reflex-dev__reflex-1369 (`56e866ec-41f7-428b-9c91-51b9787ce934`)  
Status: scored  
Gate: open  
Judge: gpt-5.6-sol  

| channel | score |
|---|--:|
| outcome | 0.8 |
| deterministic (soft) | 0.7750 |
| rubric | 0.8100 |
| **process** = (det + rubric) / 2 | 0.7925 |

| composed score | value |
|---|--:|
| **score_eval** = gate·((1−2α)·outcome + 2α·process), α=0.05 | 0.7993 |
| **score_rl** — same form over the process score normalised within this task's outcome stratum | 0.7700 |

<!-- quality -->
## Quality (publish-only, never part of reward)

Judge: gpt-5.6-sol  
Version: quality-v1, prompt 6169e82413340627  
Status: scored (shadow, uncalibrated)  

| dimension | verdict |
|---|---|
| conventions (Q1) | fail |
| minimal_diff (Q2) | pass |
| abstraction (Q3) | pass |
| readability (Q4) | fail |
| naming (Q5) | fail |
| idiomaticity (Q6) | pass |
| dead_code (Q7) | fail |
| **score_quality** = passed weight / total weight | 0.4286 |
<!-- /quality -->
