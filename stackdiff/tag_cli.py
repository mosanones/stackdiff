"""CLI for tagging and inspecting diff keys by category."""
import argparse
import json
import sys
from stackdiff.differ import diff_files
from stackdiff.diff_tags import tag_diff_keys, filter_by_tag


def build_tag_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stackdiff-tag",
        description="Tag changed keys by category (auth, network, database, ...)",
    )
    p.add_argument("staging", help="Staging config file")
    p.add_argument("production", help="Production config file")
    p.add_argument("--tag", metavar="TAG", help="Filter output to a specific tag")
    p.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt"
    )
    p.add_argument("--mask", action="store_true", help="Mask sensitive values")
    return p


def main(argv=None):
    parser = build_tag_parser()
    args = parser.parse_args(argv)

    ctx = diff_files(args.staging, args.production, mask=args.mask)
    changed_keys = list(ctx.diff.changed.keys())

    tagged = tag_diff_keys(changed_keys)

    if args.tag:
        matched = filter_by_tag(tagged, args.tag)
        if args.fmt == "json":
            print(json.dumps({"tag": args.tag, "keys": matched}, indent=2))
        else:
            if not matched:
                print(f"No keys tagged '{args.tag}'.")
            else:
                print(f"Keys tagged '{args.tag}':")
                for k in matched:
                    print(f"  - {k}")
        return

    if args.fmt == "json":
        print(json.dumps(tagged.as_dict(), indent=2))
    else:
        if not tagged.tagged_keys:
            print("No changed keys found.")
            return
        for tk in tagged.tagged_keys:
            tag_str = ", ".join(tk.tags) if tk.tags else "(untagged)"
            print(f"  {tk.key}: [{tag_str}]")


if __name__ == "__main__":
    main()
