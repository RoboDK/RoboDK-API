---
name: Rejected bug fix patterns
description: Bug fix suggestions that were explicitly rejected by the user in this repo
type: feedback
---

Do not suggest or apply these two changes in this repository:

1. **Zero-norm guard in `quaternion_2_pose()`** — Do not add a `qnorm < 1e-12` check or raise a `ValueError` before the quaternion normalization division in `robomath.py`.

2. **TypeScript number-parsing regex in `getParams()`** — Do not replace the existing `value.replace('.', '').replace('-', '').match(/^\d+$/)` check with a full numeric regex in `robodk.ts`.

**Why:** User explicitly rejected both suggestions (reverted/ignored both edits).

**How to apply:** Skip these when reviewing or fixing bugs. Do not re-propose them even if the same analysis leads there again.
