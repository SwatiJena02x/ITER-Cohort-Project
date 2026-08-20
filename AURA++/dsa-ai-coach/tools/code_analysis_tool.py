from llm import OllamaClient


class CodeAnalysisTool:
    """
    Analyzes a student's DSA code.

    Checks:
    - Correctness
    - Bugs
    - Time complexity
    - Space complexity
    - Edge cases
    - Improvements
    """

    def __init__(self):

        self.llm = OllamaClient(
            model="qwen2.5-coder:7b"
        )

    def execute(
        self,
        code: str,
        problem: str = ""
    ) -> str:

        prompt = (
            "You are an expert DSA code reviewer.\n\n"

            "Analyze the student's Python code.\n\n"

            "Problem:\n"
            + problem
            + "\n\n"

            "Student Code:\n"
            "```python\n"
            + code
            + "\n```\n\n"

            "Provide the analysis using exactly "
            "this structure:\n\n"

            "1. Correctness\n"
            "Explain whether the solution is correct.\n"
            "If it is incorrect, identify the main "
            "logical issue.\n\n"

            "2. Bugs\n"
            "Identify syntax errors, runtime errors, "
            "logical errors, or other problems.\n"
            "If there are no obvious bugs, say "
            "'No obvious bugs found.'\n\n"

            "3. Time Complexity\n"
            "Give the Big-O time complexity.\n"
            "Explain why.\n\n"

            "4. Space Complexity\n"
            "Give the Big-O space complexity.\n"
            "Explain why.\n\n"

            "5. Edge Cases\n"
            "Mention important edge cases the student "
            "should test.\n\n"

            "6. Improvement\n"
            "Explain how the solution could be improved.\n"
            "Do not immediately provide a complete "
            "solution unless necessary.\n\n"

            "Keep the explanation educational, "
            "clear, and concise."
        )

        response = self.llm.generate(
            prompt
        )

        return response