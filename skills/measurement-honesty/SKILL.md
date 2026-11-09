---
name: measurement-honesty
description: Report measured outcomes without invented precision.
---
# Measurement honesty
1. Declare source, window, sample size, consent basis, and test-vs-production status.
2. Deduplicate events before computing any rates.
3. Use stable user assignment and report each arm's denominator.
4. Treat small samples as descriptive, not significant.
5. Keep internal traffic separate. Never call a simulator a 30-day production study.
6. Propose changes for human approval; do not inject tracking into client sites.
