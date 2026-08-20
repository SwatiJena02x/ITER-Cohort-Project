# ==========================================================
# File Name:
# code_runner.py
#
# Purpose:
# ----------------------------------------------------------
# Compiles/runs submitted code in multiple languages and
# returns a uniform result dict.
#
# Supported: python, java, c, cpp (c++)
#
# Each run happens in its own temp directory so compiled
# languages (which need matching filenames, e.g. Java's
# public class name) don't collide between requests, and
# so cleanup is a single directory removal.
#
# CHANGE (for code_exec_agent integration):
# run_code() now accepts an optional `stdin_input` string,
# piped to the program's stdin. This lets callers run the
# same code once per rubric.critical_edge_case, feeding each
# case's input and comparing stdout to expected_output.
#
# SECURITY NOTE — same caveat as before, now for 4 languages
# instead of 1: this has no real sandboxing. A blocklist below
# rejects the most obvious dangerous calls per language, but
# that's a tripwire, not a sandbox. Compiled languages (C/C++)
# have full syscall access if the blocklist is bypassed — do
# not expose this publicly without running it inside an
# isolated, no-network Docker container.
# ==========================================================

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

TIMEOUT_SECONDS = 8  # compiled languages need a bit more room than pure Python

# --------------------------------------------------------
# Per-language dangerous-call blocklists.
#
# These are simple substring/regex checks, not real static
# analysis — a determined attacker can obfuscate around them.
# They exist to stop the obvious, not the clever.
# --------------------------------------------------------
BLOCKED_PATTERNS = {
    "python": [
        r"^\s*(?:import|from)\s+(os|subprocess|sys|shutil|socket|ctypes|"
        r"multiprocessing|threading|importlib|pty|signal|pickle|marshal|"
        r"resource|pathlib)\b",
    ],
    "c": [
        r"\bsystem\s*\(", r"\bpopen\s*\(", r"\bfork\s*\(",
        r"\bexecve?\w*\s*\(", r"#include\s*<unistd\.h>",
    ],
    "cpp": [
        r"\bsystem\s*\(", r"\bpopen\s*\(", r"\bfork\s*\(",
        r"\bexecve?\w*\s*\(", r"#include\s*<unistd\.h>",
        r"#include\s*<cstdlib>.*\bsystem\b",
    ],
    "java": [
        r"Runtime\s*\.\s*getRuntime\s*\(\s*\)\s*\.\s*exec",
        r"\bProcessBuilder\b",
    ],
}


def _find_blocked_pattern(code: str, language: str):
    for pattern in BLOCKED_PATTERNS.get(language, []):
        if re.search(pattern, code, re.MULTILINE):
            return pattern
    return None


def _extract_java_class_name(code: str) -> str:
    """
    Java requires the filename to match the public class name.
    Falls back to 'Main' if no public class is found (the
    subsequent compile step will surface a clear error if that
    guess is wrong).
    """
    match = re.search(r"public\s+class\s+(\w+)", code)
    return match.group(1) if match else "Main"


def _result(status: str, output: str = "", error: str = "") -> str:
    return json.dumps({"status": status, "output": output, "error": error})


def run_code(code: str, language: str, stdin_input: str = "") -> str:
    """
    Compiles (if needed) and runs `code` in `language`,
    optionally piping `stdin_input` to the program's stdin.
    Returns a JSON string: {status, output, error}.

    status is one of: passed, failed, timeout, unsupported, error
    """

    language = language.strip().lower()
    lang_aliases = {"c++": "cpp", "cplusplus": "cpp"}
    language = lang_aliases.get(language, language)

    supported = {"python", "java", "c", "cpp"}
    if language not in supported:
        return _result(
            "unsupported",
            error=f"Execution for '{language}' is not supported. "
            f"Supported languages: python, java, c, cpp.",
        )

    blocked = _find_blocked_pattern(code, language)
    if blocked:
        return _result(
            "failed",
            error="This code uses a system/process call that isn't allowed. "
            "This coach only executes pure algorithmic code — no OS, "
            "filesystem, network, or process access.",
        )

    work_dir = tempfile.mkdtemp(prefix="dsa_exec_")

    try:
        if language == "python":
            return _run_python(code, work_dir, stdin_input)
        elif language == "c":
            return _run_c(code, work_dir, stdin_input)
        elif language == "cpp":
            return _run_cpp(code, work_dir, stdin_input)
        elif language == "java":
            return _run_java(code, work_dir, stdin_input)

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


# ==========================================================
# Python
# ==========================================================

def _run_python(code: str, work_dir: str, stdin_input: str = "") -> str:
    file_path = os.path.join(work_dir, "solution.py")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        result = subprocess.run(
            [sys.executable, file_path],
            input=stdin_input,
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return _result("timeout", error=f"Execution exceeded {TIMEOUT_SECONDS}s.")

    if result.returncode == 0:
        return _result("passed", output=result.stdout.strip())
    return _result("failed", output=result.stdout.strip(), error=result.stderr.strip())


# ==========================================================
# C
# ==========================================================

def _run_c(code: str, work_dir: str, stdin_input: str = "") -> str:
    src_path = os.path.join(work_dir, "solution.c")
    bin_path = os.path.join(work_dir, "solution")

    with open(src_path, "w", encoding="utf-8") as f:
        f.write(code)

    compile_result = _compile(["gcc", src_path, "-o", bin_path, "-lm"], work_dir)
    if compile_result is not None:
        return compile_result

    return _run_binary([bin_path], work_dir, stdin_input)


# ==========================================================
# C++
# ==========================================================

def _run_cpp(code: str, work_dir: str, stdin_input: str = "") -> str:
    src_path = os.path.join(work_dir, "solution.cpp")
    bin_path = os.path.join(work_dir, "solution")

    with open(src_path, "w", encoding="utf-8") as f:
        f.write(code)

    compile_result = _compile(["g++", src_path, "-o", bin_path], work_dir)
    if compile_result is not None:
        return compile_result

    return _run_binary([bin_path], work_dir, stdin_input)


# ==========================================================
# Java
# ==========================================================

def _run_java(code: str, work_dir: str, stdin_input: str = "") -> str:
    class_name = _extract_java_class_name(code)
    src_path = os.path.join(work_dir, f"{class_name}.java")

    with open(src_path, "w", encoding="utf-8") as f:
        f.write(code)

    compile_result = _compile(["javac", src_path], work_dir)
    if compile_result is not None:
        return compile_result

    return _run_binary(["java", "-cp", work_dir, class_name], work_dir, stdin_input)


# ==========================================================
# Shared helpers
# ==========================================================

def _compile(cmd: list, work_dir: str):
    """
    Runs a compiler command. Returns None if compilation
    succeeded (caller should proceed to run the binary), or a
    JSON result string if it failed/errored/timed out.
    """
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=TIMEOUT_SECONDS, cwd=work_dir,
        )
    except subprocess.TimeoutExpired:
        return _result("timeout", error=f"Compilation exceeded {TIMEOUT_SECONDS}s.")
    except FileNotFoundError:
        return _result(
            "error",
            error=f"Compiler '{cmd[0]}' is not installed on this server. "
            f"Ask the server admin to install it.",
        )

    if result.returncode != 0:
        return _result("failed", error=result.stderr.strip() or "Compilation failed.")

    return None  # success — caller proceeds to run the binary


def _run_binary(cmd: list, work_dir: str, stdin_input: str = "") -> str:
    try:
        result = subprocess.run(
            cmd,
            input=stdin_input,
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS, cwd=work_dir,
        )
    except subprocess.TimeoutExpired:
        return _result("timeout", error=f"Execution exceeded {TIMEOUT_SECONDS}s.")
    except FileNotFoundError:
        return _result(
            "error",
            error=f"Runtime '{cmd[0]}' is not installed on this server.",
        )

    if result.returncode == 0:
        return _result("passed", output=result.stdout.strip())
    return _result("failed", output=result.stdout.strip(), error=result.stderr.strip())