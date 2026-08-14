"""Local code execution wrapper for sandboxed Python execution.

Runs user code in a subprocess with a timeout for safety.
Used as a replacement for the Piston API which is no longer publicly available.
"""
import subprocess
import json
import sys
import tempfile
import os
from pathlib import Path


async def execute_code(code: str, test_cases: list[dict], function_name: str) -> list[dict]:
    """
    Execute user code against test cases using local subprocess.
    
    For each test case, wraps the user's code with a test harness that:
    1. Defines the user's function
    2. Calls it with the test case inputs
    3. Prints the result as JSON
    
    Returns a list of {input, expected, actual, passed} dicts.
    """
    results = []

    for tc in test_cases:
        test_input = tc["input"]
        expected = tc["expected"]

        # Build the argument string from the input dict
        args = ", ".join(
            f"{k}={json.dumps(v)}" for k, v in test_input.items()
        )

        # Wrap user code with test harness
        full_code = f"""{code}

import json
try:
    result = {function_name}({args})
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
"""

        try:
            # Write code to a temp file and execute it
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False, encoding='utf-8'
            ) as tmp:
                tmp.write(full_code)
                tmp_path = tmp.name

            try:
                # Run with the same Python interpreter, with a timeout
                result_proc = subprocess.run(
                    [sys.executable, tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=tempfile.gettempdir(),
                )

                stdout = result_proc.stdout.strip()
                stderr = result_proc.stderr.strip()

                if stderr and not stdout:
                    actual = f"Error: {stderr[:200]}"
                    passed = False
                elif stdout:
                    try:
                        actual = json.loads(stdout)
                        # Handle list comparison (order might differ for some problems)
                        if isinstance(expected, list) and isinstance(actual, list):
                            passed = sorted(map(str, actual)) == sorted(map(str, expected))
                        else:
                            passed = actual == expected
                    except (json.JSONDecodeError, ValueError):
                        actual = stdout
                        passed = False
                else:
                    actual = "No output"
                    passed = False

            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        except subprocess.TimeoutExpired:
            actual = "Execution timed out (10s limit)"
            passed = False
        except Exception as e:
            actual = f"Execution error: {str(e)}"
            passed = False

        results.append({
            "input": test_input,
            "expected": expected,
            "actual": actual,
            "passed": passed,
        })

    return results


def extract_function_name(starter_code: str) -> str:
    """Extract the function name from the starter code."""
    for line in starter_code.split("\n"):
        line = line.strip()
        if line.startswith("def "):
            # Extract function name between 'def ' and '('
            name = line[4:line.index("(")]
            return name.strip()
    return "solution"
