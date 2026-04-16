# stackdiff

A CLI tool to compare environment configs across staging and production deployments.

## Installation

```bash
pip install stackdiff
```

## Usage

Compare environment configurations between two deployments:

```bash
stackdiff staging production
```

Specify a config file or environment source:

```bash
stackdiff --env-file .env.staging --compare .env.production
stackdiff --stack my-app --format json
```

Example output:

```
[~] DATABASE_URL   staging: postgres://db-staging/app
                   production: postgres://db-prod/app
[+] NEW_FEATURE_FLAG  only in: production
[-] DEBUG             only in: staging
```

### Options

| Flag | Description |
|------|-------------|
| `--format` | Output format: `text`, `json`, `yaml` |
| `--ignore` | Comma-separated list of keys to ignore |
| `--no-color` | Disable colored output |
| `--quiet` | Show only differences |

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.

## License

[MIT](LICENSE)