# Score — opus-5/run_1

Task: dgtlmoon__changedetection.io-3433 (`8ab81969-37a0-4f3b-86af-d21560f386ce`)  
Status: scored  
Gate: open  
Judge: gpt-5.6-sol  

| channel | score |
|---|--:|
| outcome | 0.94 |
| deterministic (soft) | 0.2941 |
| rubric | 0.4765 |
| **process** = (det + rubric) / 2 | 0.3853 |

| composed score | value |
|---|--:|
| **score_eval** = gate·((1−2α)·outcome + 2α·process), α=0.013889 | 0.9246 |
| **score_rl** — same form over the process score normalised within this task's outcome stratum | 0.9278 |

<!-- quality -->
## Quality (publish-only, never part of reward)

Judge: gpt-5.6-sol  
Version: quality-v1, prompt 6169e82413340627  
Status: scored (shadow, uncalibrated)  

| dimension | verdict |
|---|---|
| conventions (Q1) | fail |
| minimal_diff (Q2) | fail |
| abstraction (Q3) | pass |
| readability (Q4) | pass |
| naming (Q5) | fail |
| idiomaticity (Q6) | pass |
| dead_code (Q7) | fail |
| **score_quality** = passed weight / total weight | 0.4286 |
<!-- /quality -->
