"""AST-based anti-pattern detection engine.

Parses submitted Python code and checks it against a problem's anti_patterns
rules using the `ast` module. Fully deterministic — no LLM calls here.
"""
import ast
from typing import Optional


def _count_nested_for_loops(tree: ast.AST) -> int:
    """Count the maximum nesting depth of for-loops."""
    max_depth = 0

    def _walk(node: ast.AST, depth: int = 0):
        nonlocal max_depth
        if isinstance(node, (ast.For, ast.AsyncFor)):
            depth += 1
            max_depth = max(max_depth, depth)
        for child in ast.iter_child_nodes(node):
            _walk(child, depth)

    _walk(tree)
    return max_depth


def _has_dict_or_set_usage(tree: ast.AST) -> bool:
    """Check if the code uses dict or set (via constructor, literal, or comprehension)."""
    for node in ast.walk(tree):
        # Dict literal or comprehension
        if isinstance(node, (ast.Dict, ast.DictComp, ast.Set, ast.SetComp)):
            return True
        # dict() or set() constructor call
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ("dict", "set"):
                return True
    return False


def _has_list_or_stack_usage(tree: ast.AST) -> bool:
    """Check if code uses a list as a stack (append/pop calls)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ("append", "pop"):
                    return True
    return False


def _uses_sorted(tree: ast.AST) -> bool:
    """Check if code calls sorted() or .sort()."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "sorted":
                return True
            if isinstance(node.func, ast.Attribute) and node.func.attr == "sort":
                return True
    return False


def _uses_string_replace_in_loop(tree: ast.AST) -> bool:
    """Check if code uses str.replace() inside a while loop."""
    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute):
                        if child.func.attr == "replace":
                            return True
    return False


def _has_counter_usage(tree: ast.AST) -> bool:
    """Check if code uses Counter or manual character counting with a dict."""
    for node in ast.walk(tree):
        # Counter()
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "Counter":
                return True
            if isinstance(node.func, ast.Attribute) and node.func.attr == "Counter":
                return True
    # Also check for dict-based counting
    return _has_dict_or_set_usage(tree)


# ─── Rule checkers ──────────────────────────────────────────────────────
# Each rule returns a matched anti-pattern dict if triggered, else None.

def _check_nested_loop_over_same_array(tree: ast.AST, anti_pattern: dict) -> Optional[dict]:
    """Trigger if there are 2+ nested for-loops and no dict/set usage."""
    if _count_nested_for_loops(tree) >= 2 and not _has_dict_or_set_usage(tree):
        return anti_pattern
    return None


def _check_string_replace_loop(tree: ast.AST, anti_pattern: dict) -> Optional[dict]:
    """Trigger if str.replace() is used inside a while loop."""
    if _uses_string_replace_in_loop(tree) and not _has_list_or_stack_usage(tree):
        return anti_pattern
    return None


def _check_uses_sorted_for_comparison(tree: ast.AST, anti_pattern: dict) -> Optional[dict]:
    """Trigger if sorted() is used and no Counter/dict frequency counting."""
    if _uses_sorted(tree) and not _has_counter_usage(tree):
        return anti_pattern
    return None


# Map rule names to checker functions
RULE_CHECKERS = {
    "nested_loop_over_same_array": _check_nested_loop_over_same_array,
    "string_replace_loop": _check_string_replace_loop,
    "uses_sorted_for_comparison": _check_uses_sorted_for_comparison,
}


def _pad_incomplete_code(code: str) -> str:
    """Add `pass` to incomplete blocks so ast.parse succeeds on in-progress code.
    
    When a user presses Enter after `for i in range(n):`, the code has an empty
    block body which causes SyntaxError. We detect the last non-empty line's
    indentation and append `pass` with one extra indent level.
    """
    lines = code.rstrip().split('\n')
    if not lines:
        return code
    
    last_line = lines[-1]
    stripped = last_line.rstrip()
    
    # If last line ends with ':', it needs a body
    if stripped.endswith(':'):
        indent = len(last_line) - len(last_line.lstrip())
        return code + '\n' + ' ' * (indent + 4) + 'pass'
    
    return code


def analyze_code(code: str, anti_patterns: list[dict]) -> Optional[dict]:
    """
    Parse the submitted code and check against the problem's anti-pattern rules.
    
    Returns the first matched anti-pattern dict, or None if no patterns detected.
    """
    # Pad incomplete blocks so we can still analyze partial code
    padded_code = _pad_incomplete_code(code)
    
    try:
        tree = ast.parse(padded_code)
    except SyntaxError:
        # Code is truly broken, can't analyze
        return None

    for pattern in anti_patterns:
        rule_name = pattern["rule"]
        checker = RULE_CHECKERS.get(rule_name)
        if checker:
            result = checker(tree, pattern)
            if result is not None:
                return result

    return None
