# Versioning and tracing — Stage 7: Operate

## Versioning
Every agent variant, the decision tree, and the ontology are plain files
under version control. A release is a git tag; a rollback is `git checkout
<tag> -- <path>` (or, in a CI pipeline, redeploying the previous container
image). There is deliberately no separate "model registry" for this kit —
the tree, the ontology and the prompts are small enough that the version
history of the repository *is* the model registry.

**Recommended tags**, matching the eval baseline they were scored against:
`v1-ungrounded-baseline`, `v1-grounded-raw`, `v1-grounded-semantic`.

## Tracing
`apextel/recorder.py` (used by every grounded agent) writes one JSON line
per model call and per turn to `runs.jsonl`:

```json
{"time": "2026-08-10T14:12:03+00:00", "session": "abc123", "agent": "v1_grounded_semantic", "event": "model_call", "input_tokens": 1840, "output_tokens": 92}
{"time": "2026-08-10T14:12:04+00:00", "session": "abc123", "agent": "v1_grounded_semantic", "event": "turn", "seconds": 1.3}
```

This is what makes Stage 6's token comparison possible, and what an
operator would tail in production to see the agent's real call volume.

## Rollback
See [`fire_drill.py`](fire_drill.py) — it doesn't just describe rollback, it
performs one: injects a real bug into Stage 2's decision tree, proves the
Stage 2 test suite catches it, rolls the file back, and proves the suite is
green again. Run it yourself:

```bash
cd stages/stage7_operate
python3 fire_drill.py
```

> **Expected:** `DRILL PASSED`, with a timing breakdown of detect vs.
> rollback vs. confirm. On this machine that's a few hundredths of a second
> because the "deploy" is a file write — in a real CI/CD pipeline the same
> shape of drill would time the actual build-test-rollback cycle.
