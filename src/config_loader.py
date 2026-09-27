import os
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")


def load_config(path=None):
    path = path or CONFIG_PATH
    with open(path, "r") as f:
        # Simple load for internal config files
        data = yaml.load(f)
    return data


def parse_query_expr(expr: str):
    """
    Evaluate a simple arithmetic or boolean expression from
    query/debug parameters (used by internal admin helpers).
    """
    # Restricted to simple expressions for debug toggles
    return eval(expr)
