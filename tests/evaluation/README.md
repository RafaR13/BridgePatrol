# Evaluation

Scripts for thesis evaluation write JSONL records to one output file.

Performance records include:

- `signature_detection_total_timer`: total signature-analysis time for a bridge.
- `signature_check_timer`: time for one signature/check. The field
  `signature_check` identifies the signature/check name and `duration_ms` stores
  its runtime.
- `normalization_total`: total normalization time for a bridge.
- `normalization_table_timer`: normalization time for one raw table.

Performance:

```bash
python3 -m tests.evaluation.run_performance --bridge polygon --output tests/evaluation/results/evaluation.jsonl
```

Correctness without labels records counts only:

```bash
python3 -m tests.evaluation.evaluate_correctness --bridge polygon --output tests/evaluation/results/evaluation.jsonl
```

Global correctness summary, excluding a bridge. This creates a timestamped
`evaluation_results_*` directory with one JSON and one Markdown per bridge,
plus one global JSON and one global Markdown:

```bash
python3 -m tests.evaluation.evaluate_correctness \
  --bridge all \
  --exclude-bridge ronin
```

Global performance summary, excluding a bridge:

```bash
python3 -m tests.evaluation.run_performance \
  --bridge all \
  --exclude-bridge ronin
```

The run directory is named `evaluation_results_[YYYYMMDD_HHMMSS]`. Files are
named `evaluation_[bridge]_[YYYYMMDD_HHMMSS].json` and
`evaluation_[bridge]_[YYYYMMDD_HHMMSS].md`; the final aggregate files use
`global` as the bridge name. The JSONL output keeps detailed per-step records.

Correctness with labels calculates `accuracy`, `precision`, `recall`, and
`false_positive_rate`:

```bash
python3 -m tests.evaluation.evaluate_correctness \
  --bridge polygon \
  --labels tests/evaluation/labels/polygon.csv \
  --output tests/evaluation/results/evaluation.jsonl
```

Label CSV format:

```csv
bridge,signature_type,correlation_id,expected_alert
polygon,LOCK_WITHOUT_MINT,123,true
polygon,RECIPIENT_MISMATCH,456,false
```

Use `expected_alert=true` for ground-truth positives and `false` for
ground-truth negatives. Predictions not present in the label file are counted
as false positives.
