# Score — opus-5/run_7

Task: dgtlmoon__changedetection.io-3433 (`8ab81969-37a0-4f3b-86af-d21560f386ce`)  
Status: scored  
Gate: open  
Judge: gpt-5.6-sol  

| channel | score |
|---|--:|
| outcome | 0.06 |
| deterministic (soft) | 0.2903 |
| rubric | 0.3975 |
| **process** = (det + rubric) / 2 | 0.3439 |

| composed score | value |
|---|--:|
| **score_eval** = gate·((1−2α)·outcome + 2α·process), α=0.013889 | 0.0679 |
| **score_rl** — same form over the process score normalised within this task's outcome stratum | 0.0583 |

<!-- quality -->
## Quality (publish-only, never part of reward)

Judge: gpt-5.6-sol  
Version: quality-v1, prompt 6169e82413340627  
Status: scored (shadow, uncalibrated)  

| dimension | verdict |
|---|---|
| conventions (Q1) | pass |
| minimal_diff (Q2) | fail |
| abstraction (Q3) | fail |
| readability (Q4) | pass |
| naming (Q5) | pass |
| idiomaticity (Q6) | pass |
| dead_code (Q7) | pass |
| **score_quality** = passed weight / total weight | 0.7143 |
<!-- /quality -->
