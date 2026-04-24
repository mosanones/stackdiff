# Diff Normalizer

The `diff_normalizer` module pre-processes flat config dictionaries before they
are compared, ensuring that superficial formatting differences do not produce
false positives in the diff output.

## Features

| Option | Default | Description |
|---|---|---|
| `strip_whitespace` | `True` | Trim leading/trailing spaces from string values |
| `coerce_booleans` | `True` | Convert `"true"`, `"yes"`, `"1"`, `"on"` → `True` and their opposites → `False` |
| `coerce_numbers` | `True` | Parse numeric strings to `int` or `float` |
| `lowercase_keys` | `False` | Lowercase all keys before comparison |
| `aliases` | `{}` | Map old key names to canonical names |

## Usage

```python
from stackdiff.diff_normalizer import NormalizeOptions, normalize_config, normalize_pair

opts = NormalizeOptions(
    strip_whitespace=True,
    coerce_booleans=True,
    coerce_numbers=True,
    lowercase_keys=True,
    aliases={"db_host": "database.host"},
)

result = normalize_config(raw_flat_cfg, opts)
print(result.config)    # normalized dict
print(result.changes)   # list of human-readable change descriptions
```

To normalize both sides of a comparison at once:

```python
left_norm, right_norm = normalize_pair(staging_cfg, production_cfg, opts)
```

## Integration with the pipeline

`normalize_pair` is called inside `run_pipeline` when `normalize=True` is
passed, before `diff_configs` runs. This prevents noise from environment
variables that store booleans as `"true"` in one deployment and `True` in
another.

## Change log

Each `NormalizeResult` exposes a `changes` list so you can audit exactly what
was coerced or renamed:

```
port: '8080' -> 8080
debug: 'true' -> True
alias: db_host -> database.host
```
