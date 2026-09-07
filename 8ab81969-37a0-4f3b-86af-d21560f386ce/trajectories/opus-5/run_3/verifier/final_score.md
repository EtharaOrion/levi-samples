# Score — opus-5/run_3

Task: dgtlmoon__changedetection.io-3433 (`8ab81969-37a0-4f3b-86af-d21560f386ce`)  
Status: scored  
Gate: open  
Judge: gpt-5.6-sol  

| channel | score |
|---|--:|
| outcome | 0.06 |
| deterministic (soft) | 0.3226 |
| rubric | 0.3842 |
| **process** = (det + rubric) / 2 | 0.3534 |

| composed score | value |
|---|--:|
| **score_eval** = gate·((1−2α)·outcome + 2α·process), α=0.013889 | 0.0682 |
| **score_rl** — same form over the process score normalised within this task's outcome stratum | 0.0609 |

<!-- quality -->
## Quality (publish-only, never part of reward)

Judge: gpt-5.6-sol  
Version: quality-v1, prompt 6169e82413340627  
Status: scored (shadow, uncalibrated)  

| dimension | verdict |
|---|---|
| conventions (Q1) | fail |
| minimal_diff (Q2) | fail |
| abstraction (Q3) | fail |
| readability (Q4) | pass |
| naming (Q5) | pass |
| idiomaticity (Q6) | pass |
| dead_code (Q7) | fail |
| **score_quality** = passed weight / total weight | 0.4286 |
<!-- /quality -->
