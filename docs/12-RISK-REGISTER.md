# Risk Register

## Ranked by Severity × Probability

| # | Risk | Severity | Probability | Mitigation |
|---|---|---|---|---|
| 1 | **Zero git commits → disqualification** | Fatal | **HIGH (currently)** | Commit in next 5 minutes |
| 2 | **Video link inaccessible → disqualification** | Fatal | Medium | Test from incognito at hour 20 |
| 3 | **Single code dump → disqualification** | Fatal | Medium | Commit every 45 min, push every 2h |
| 4 | **Member 3 absent from git log → Grand Final fail** | Fatal | Medium | Assign him 5 doc/test commits |
| 5 | **Alternate dataset crashes → Grand Final fail** | Severe | Medium | Test `seed=999` at hour 20 |
| 6 | **XGBoost AUC too low** | Moderate | Medium | Fallback: drop ML, use rules+baseline+complaint+graph |
| 7 | **Rich rendering broken on projector** | Moderate | Low | Test 3 terminals, `width=100`, plain-text fallback |
| 8 | **Money trail BFS slow** | Moderate | Low | Cap hops=5, time window filter |
| 9 | **Complaint regex misses variants** | Moderate | Medium | Unit test with 20 real NCRP examples |
| 10 | **Fusion weights feel arbitrary** | Low | High | Document weights, avoid overclaiming precision |
| 11 | **Run out of time for polish** | Moderate | High | Stop coding at hour 28, buffer for polish |
| 12 | **Team member sick / unavailable** | Moderate | Low | Other member picks up their open commit list |
| 13 | **Fusion formula produces unrealistic scores** | Moderate | Medium | Sanity-check top 20 vs. manual inspection |
| 14 | **PDF generation fails on edge case** | Moderate | Low | Test 5 accounts before hour 30 |
| 15 | **Alternate dataset schema mismatch** | Severe | Medium | Lock schema in README; test loader early |

## Early-Warning Signals

Watch for these signs — they precede the above risks:

- Person A or B hasn't committed in 2+ hours → **commit discipline slipping**
- Data generator not producing expected counts → **fall back to fixed CSV**
- XGBoost training loss not decreasing → **features are noise, switch to rules**
- Frontend not rendering Account 360 by hour 24 → **dedicate both members**
- Video not started by hour 26 → **Person C owns it, record immediately**
- 12:00 AM has < 15 commits → **stop features, catch up on git**

## Contingency Plans

### If XGBoost fails (AUC < 0.75)

**Fallback:** Drop ML layer. Reweight fusion:

```python
WEIGHTS = {'rule': 0.30, 'baseline': 0.30, 'complaint': 0.25, 'graph': 0.15, 'ml': 0.0}
```

Still covers all 6 PS asks — ML is not the only differentiator.

### If complaint correlator fails entity resolution

**Fallback:** Exact UPI match only (no fuzzy). Recall drops ~30%, but pipeline works. Judges see a working demo — better than a broken smarter one.

### If terminal renders badly

**Fallback:** `Console(force_terminal=True, color_system=None)` → plain ASCII output. Still demoable.

### If alternate dataset crashes

**Fallback:** Freeze loader schema. Log the crash in README as "known limitation — schema requires X". Better to disclose than have judges discover on 27 Nov.

### If Person C is unreachable

**Fallback:** Person A records video. Sacrifice 2h of coding to do it. Video is a hard requirement.

## Recovery Protocols

### If a critical bug appears at hour 32

1. **Do not debug** — revert to last known-good commit
2. **Document the bug** in README
3. **Continue video recording** with the reverted version
4. **Note it in Q&A prep**: "Known limitation, planned fix in production roadmap"

### If a team member is unavailable > 2h

1. **Take over their open task list** (visible in commit messages)
2. **Reduce their assignment**: only doc + test commits when they return
3. **Continue** — do not wait

### If the deadline is 2h away and video isn't uploaded

1. Record a 9-minute version immediately (do not polish)
2. Upload to Google Drive
3. Verify viewer access from incognito
4. Submit URL on portal
5. **Then** — if time remains — replace with a better version