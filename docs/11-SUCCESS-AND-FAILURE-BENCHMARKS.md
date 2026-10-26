# Success and Failure Benchmarks

## Success Criteria (What We Must Hit)

### Functional Success

| Criterion | Success Threshold | Measurement |
|---|---|---|
| End-to-end demo path works | All 8 screens reachable, no crashes | Manual demo rehearsal |
| Detection on fixed case | Ring of 12 flagged as HIGH or CRITICAL | `ACC-*` top-20 rank check |
| Complaint correlation | ≥ 15/23 complaints auto-linked | Precision check |
| Money trail | ≥ 3-hop trace on ring origin | BFS output inspection |
| PDF report | Generates with SHA-256, no errors | Run on 5 accounts |
| Alternate dataset | Full pipeline runs on `seed=999` | Person C test at hour 20 |
| Cold-start handling | New accounts don't crash scorer | Create a 5-day-old account, score it |

### Non-Functional Success

| Criterion | Success Threshold |
|---|---|
| Startup time | < 5 seconds |
| Screen render | < 500 ms |
| Score lookup | < 200 ms |
| Money trail (5 hops) | < 5 seconds |
| PDF generation | < 10 seconds |
| Cross-platform | Runs on Windows + Linux |

### Submission Success

| Criterion | Success Threshold |
|---|---|
| Git commits | ≥ 60, iterative, meaningful messages |
| All 3 members in git log | Yes |
| Video length | Between 8 and 10 minutes |
| Video link works | Verified from incognito |
| Portal URL submitted | Before 11:59 PM |
| Repo private + collaborators | Verified |

## Failure Benchmarks (What Disqualifies Us)

### Fatal Failures

| Failure | Why Fatal | Prevention |
|---|---|---|
| Zero commits in first hour | Disqualification | Commit in next 5 minutes |
| Single code dump commit | Disqualification | Commit every 45 min |
| Commit after 11:59 PM | Disqualification | Freeze code at hour 28 |
| Video link inaccessible | Disqualification | Test from incognito at hour 20 |
| Video < 8 min or > 10 min | Disqualification | Target 9:00 |
| Member missing from git log | Grand Final defense fails | Person C commits docs + tests |
| Alternate dataset crashes | Grand Final demo fails | Person C tests at hour 20 |
| Repo not private | Rule violation | Double-check at hour 0 |

### Serious Failures (Cause Point Loss)

| Failure | Impact | Prevention |
|---|---|---|
| Demo crashes on judge's machine | Severe | Test on 3 terminals, use `width=100` |
| No explanation on alerts | Poor PS alignment | 100% coverage enforced |
| Hardcoded account IDs in code | Alternate dataset fails | Config-driven design |
| No complaint correlation demo | Missing 1 of 6 PS asks | Build it first, not last |
| No money trail in demo | Missing 1 of 6 PS asks | Prioritise the tracer |

### Soft Failures (Drop Points)

| Failure | Impact | Prevention |
|---|---|---|
| Slow money trail | Judge notices lag | Cap hops at 5, add time-window filter |
| ASCII graph illegible | Poor demo quality | Save PNG for complex cases |
| Score distributions unrealistic | Judge loses trust | Calibrate on synthetic data |
| No Hindi labels | Loses local relevance | 30 min add |

## Scoring Rubric (Judge Perspective)

Typical judging dimensions and how we score:

| Dimension | Weight (typical) | Our Score Target |
|---|---|---|
| Problem relevance | 20% | 5/5 — directly maps to PS-01 |
| Innovation | 20% | 4/5 — complaint correlator + money trail are unique |
| Technical architecture | 20% | 4/5 — 5-layer fusion + graph features |
| Functionality | 20% | 4/5 — end-to-end demo works |
| Demonstration quality | 20% | 5/5 — polished terminal + clear narrative |

**Realistic total: ~4.4/5 → shortlist likely → top 5 plausible.**

## Kill Switch Benchmarks (Decision Points)

| Checkpoint | If Failing |
|---|---|
| **C1 (Hour 1)**: No commits | STOP — fix git first |
| **C2 (Hour 6)**: No data generator | Fall back to hardcoded JSON |
| **C3 (Hour 12)**: Rules + baseline broken | Drop the ML layer, use rules + baseline |
| **C4 (Hour 18)**: RandomForest AUC < 0.75 | Drop ML layer entirely |
| **C5 (Hour 20)**: Alternate dataset fails | Hardcode-fix loader, ship |
| **C6 (Hour 24)**: Account 360 broken | Stop all features, polish this screen only |
| **C7 (Hour 26)**: No video started | Person C records immediately |
| **C8 (Hour 28)**: STOP CODING | — |
| **C9 (Hour 32)**: No video uploaded | Record 6-min fallback, extend with slides |
| **C10 (Hour 33)**: URL not submitted | Submission is now the only task |