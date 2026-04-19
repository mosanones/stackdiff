# Diff Tags

The **diff tags** feature automatically categorises changed config keys into semantic groups such as `auth`, `database`, `network`, `feature_flag`, and `logging`.

## How it works

When a diff is computed, `tag_diff_keys()` inspects each changed key name against a set of built-in pattern rules. Keys can match multiple tags.

### Built-in tag rules

| Tag | Patterns matched |
|---|---|
| `database` | `db_`, `database`, `postgres`, `mysql`, `redis` |
| `auth` | `secret`, `token`, `password`, `api_key`, `auth` |
| `network` | `host`, `port`, `url`, `endpoint`, `addr` |
| `feature_flag` | `flag_`, `feature_`, `enable_`, `disable_` |
| `logging` | `log_`, `logging`, `loglevel`, `log_level` |

## CLI usage

```bash
# Show all changed keys with their tags
stackdiff-tag staging.yaml production.yaml

# Filter to a specific tag
stackdiff-tag staging.yaml production.yaml --tag auth

# JSON output
stackdiff-tag staging.yaml production.yaml --format json

# Mask sensitive values
stackdiff-tag staging.yaml production.yaml --mask
```

## Python API

```python
from stackdiff.diff_tags import tag_diff_keys, filter_by_tag

tagged = tag_diff_keys(changed_keys, extra_rules={"cache": ["cache_"]})
auth_keys = filter_by_tag(tagged, "auth")
```

## Custom rules

Pass `extra_rules` as a `dict[str, list[str]]` to extend or override built-in patterns.
