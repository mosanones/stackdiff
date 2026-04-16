"""High-level pipeline that wires loader → filter → mask → sort → diff."""
from typing import Optional, List
from stackdiff.config_loader import load_config
from stackdiff.filter import apply_filters
from stackdiff.masker import mask_config
from stackdiff.sorter import sort_flat_config, sort_diff_result, SORT_KEY
from stackdiff.diff_engine import diff_configs, DiffResult


def run_pipeline(
    path_a: str,
    path_b: str,
    label_a: str = "A",
    label_b: str = "B",
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    mask: bool = True,
    sort_keys: bool = True,
    sort_mode: str = SORT_KEY,
    sort_reverse: bool = False,
) -> DiffResult:
    """Load two configs and return a sorted, filtered, masked DiffResult."""
    cfg_a = load_config(path_a)
    cfg_b = load_config(path_b)

    cfg_a = apply_filters(cfg_a, include=include, exclude=exclude)
    cfg_b = apply_filters(cfg_b, include=include, exclude=exclude)

    if mask:
        cfg_a = mask_config(cfg_a)
        cfg_b = mask_config(cfg_b)

    if sort_keys:
        cfg_a = sort_flat_config(cfg_a)
        cfg_b = sort_flat_config(cfg_b)

    result = diff_configs(cfg_a, cfg_b, label_a=label_a, label_b=label_b)

    result = sort_diff_result(result, mode=sort_mode, reverse=sort_reverse)
    return result
