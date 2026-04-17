# Diff Scorer

The `stackdiff.scorer` module assigns a numeric risk score to a diff result,
helping you quickly gauge how significant the differences are between two
environment configs.

## Scoring model

Each changed key contributes points based on its severity (derived from
annotations):

| Severity | Points |
|----------|--------|
| CRITICAL | 10     |
| HIGH     | 5      |
| MEDIUM   | 2      |
| LOW      | 1      |

The sum of all points becomes the **total score**, which maps to a label:

| Score range | Label      |
|-------------|------------|
| 0           | clean      |
| 1 – 9       | low-risk   |
| 10 – 29     | moderate   |
| 30+         | high-risk  |

## API

### `score_annotated(annotated: AnnotatedDiff) -> DiffScore`

Score a diff that has already been passed through the annotator. Produces
fine-grained per-severity counts.

```python
from stackdiff.annotator import annotate
from stackdiff.scorer import score_annotated

ann = annotate(diff)
result = score_annotated(ann)
print(result.label, result.total)
```

### `score_diff(diff: DiffResult) -> DiffScore`

Lightweight scoring without annotations. Every changed key counts as LOW
severity. Useful for quick checks.

```python
from stackdiff.scorer import score_diff

result = score_diff(diff)
print(result.as_dict())
```

## `DiffScore` fields

- `total` – weighted score
- `critical`, `high`, `medium`, `low` – per-severity key counts
- `label` – human-readable risk label
- `as_dict()` – serialise to a plain dictionary (useful for JSON export)
