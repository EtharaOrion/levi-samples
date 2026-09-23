# Score — zai__glm-5.3/run_1

Task: reflex-dev__reflex-977cc6990f22 (`873914cf-93b2-57a0-a5c8-264bfa2d3b66`)  
Status: scored  
Gate: open  
Judge: gpt-5.6-sol  

| channel | score |
|---|--:|
| outcome | 0.875 |
| deterministic (soft) | 0.3750 |
| rubric | 0.6871 |
| **process** = (det + rubric) / 2 | 0.5311 |

| composed score | value |
|---|--:|
| **score_eval** = gate·((1−2α)·outcome + 2α·process), α=0.05 | 0.8406 |
| **score_rl** — same form over the process score normalised within this task's outcome stratum | 0.8375 |
