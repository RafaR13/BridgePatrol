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
