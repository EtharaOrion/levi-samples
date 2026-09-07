# Score — opus-5/run_2

Task: dgtlmoon__changedetection.io-594 (`5fee266c-fa53-41c7-bdbd-285e188670ac`)  
Status: scored  
Gate: open  
Judge: gpt-5.6-sol  

| channel | score |
|---|--:|
| outcome | 0.05 |
| deterministic (soft) | 0.8205 |
| rubric | 0.7964 |
| **process** = (det + rubric) / 2 | 0.8085 |

| composed score | value |
|---|--:|
| **score_eval** = gate·((1−2α)·outcome + 2α·process), α=0.013158 | 0.0700 |
| **score_rl** — same form over the process score normalised within this task's outcome stratum | 0.0750 |

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
| readability (Q4) | fail |
| naming (Q5) | fail |
| idiomaticity (Q6) | pass |
| dead_code (Q7) | fail |
| **score_quality** = passed weight / total weight | 0.2857 |
<!-- /quality -->
