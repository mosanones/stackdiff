# Diff Search

The `diff_search` module lets you query a `DiffResult` by key pattern, value substring, or change type.

## Usage

```python
from stackdiff.diff_search import SearchQuery, search_diff

result = search_diff(diff, SearchQuery(
    key_pattern="db.*",
    change_type="changed",
    value_contains="prod",
))

print(result.count())       # number of matches
print(result.as_dict())     # serialisable output
```

## SearchQuery fields

| Field | Type | Description |
|---|---|---|
| `key_pattern` | `str` (glob) | Filter keys with `fnmatch` |
| `value_contains` | `str` | Case-insensitive substring match on value |
| `change_type` | `str` | One of `added`, `removed`, `changed` |

All fields are optional. Omitting a field means no filtering on that dimension.

## SearchResult

- `matches` — dict of `{key: {"change_type": ..., "value": ...}}`
- `count()` — number of matched keys
- `as_dict()` — serialisable representation including `count`

## Integration

Pass any `DiffResult` produced by `diff_engine.diff_configs` or `differ.diff_files` directly into `search_diff`.
