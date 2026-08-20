from problems.problem_bank import PROBLEMS


class HintTool:
    """
    Provides progressive hints for DSA problems.
    """

    def __init__(self):
        self.problems = PROBLEMS

    def get_problem(
        self,
        problem_id: str
    ) -> dict | None:

        for problem in self.problems:

            if problem["id"] == problem_id:
                return problem

        return None

    def get_hints(
        self,
        problem_id: str
    ) -> list[str]:

        problem = self.get_problem(
            problem_id
        )

        if problem is None:
            return []

        return problem.get(
            "hints",
            []
        )

    def execute(
        self,
        problem_id: str,
        hint_level: int = 1
    ) -> str:
        """
        Return a progressive hint.

        hint_level:
            1 -> first hint
            2 -> second hint
            3 -> third hint
        """

        hints = self.get_hints(
            problem_id
        )

        if not hints:

            return (
                "No hints are available "
                "for this problem."
            )

        # Make sure hint level is valid
        if hint_level < 1:
            hint_level = 1

        if hint_level > len(hints):
            hint_level = len(hints)

        hint = hints[
            hint_level - 1
        ]

        return (
            f"Hint {hint_level}: {hint}"
        )