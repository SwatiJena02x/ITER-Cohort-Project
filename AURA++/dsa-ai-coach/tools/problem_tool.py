class ProblemTool:
    """
    DSA Problem Tool.

    Selects problems based on topic/difficulty
    and avoids repeatedly returning the same problem
    during the same session.
    """

    def __init__(self):

        self.problems = [

            # ==================================================
            # DYNAMIC PROGRAMMING
            # ==================================================

            {
                "id": "dp_001",
                "title": "House Robber",
                "topic": "dynamic_programming",
                "difficulty": "medium",
                "description": (
                    "You are given an integer array nums "
                    "representing the amount of money in each house. "
                    "You cannot rob two adjacent houses. "
                    "Return the maximum amount of money you can rob."
                )
            },

            {
                "id": "dp_002",
                "title": "Climbing Stairs",
                "topic": "dynamic_programming",
                "difficulty": "medium",
                "description": (
                    "You are climbing a staircase. "
                    "It takes n steps to reach the top. "
                    "Each time you can either climb 1 or 2 steps. "
                    "Return the number of distinct ways you can climb "
                    "to the top."
                )
            },

            {
                "id": "dp_003",
                "title": "Coin Change",
                "topic": "dynamic_programming",
                "difficulty": "medium",
                "description": (
                    "You are given an integer array coins representing "
                    "coins of different denominations and an integer "
                    "amount representing a total amount of money. "
                    "Return the fewest number of coins that you need "
                    "to make up that amount. "
                    "If that amount cannot be made up, return -1."
                )
            },

            {
                "id": "dp_004",
                "title": "Longest Increasing Subsequence",
                "topic": "dynamic_programming",
                "difficulty": "medium",
                "description": (
                    "Given an integer array nums, return the length "
                    "of the longest strictly increasing subsequence."
                )
            },

            {
                "id": "dp_005",
                "title": "Partition Equal Subset Sum",
                "topic": "dynamic_programming",
                "difficulty": "medium",
                "description": (
                    "Given an integer array nums, return true if you "
                    "can partition the array into two subsets such "
                    "that the sum of the elements in both subsets "
                    "is equal."
                )
            },

            # ==================================================
            # ARRAYS
            # ==================================================

            {
                "id": "arr_001",
                "title": "Two Sum",
                "topic": "arrays",
                "difficulty": "easy",
                "description": (
                    "Given an array of integers nums and an integer "
                    "target, return indices of the two numbers such "
                    "that they add up to target."
                )
            },

            {
                "id": "arr_002",
                "title": "Product of Array Except Self",
                "topic": "arrays",
                "difficulty": "medium",
                "description": (
                    "Given an integer array nums, return an array "
                    "answer such that answer[i] is equal to the "
                    "product of all elements of nums except nums[i]. "
                    "You must solve it without using division."
                )
            },

            # ==================================================
            # STRINGS
            # ==================================================

            {
                "id": "str_001",
                "title": "Longest Substring Without Repeating Characters",
                "topic": "strings",
                "difficulty": "medium",
                "description": (
                    "Given a string s, find the length of the longest "
                    "substring without repeating characters."
                )
            },

            {
                "id": "str_002",
                "title": "Valid Anagram",
                "topic": "strings",
                "difficulty": "easy",
                "description": (
                    "Given two strings s and t, return true if t is "
                    "an anagram of s, and false otherwise."
                )
            }
        ]

    # ==========================================================
    # EXECUTE
    # ==========================================================

    def execute(
        self,
        topic=None,
        difficulty=None,
        exclude_ids=None
    ):
        """
        Return matching problems.

        exclude_ids:
            Problem IDs that should not be returned.
        """

        if exclude_ids is None:
            exclude_ids = set()

        else:
            exclude_ids = set(
                exclude_ids
            )

        # ==================================================
        # FILTER
        # ==================================================

        matches = []

        for problem in self.problems:

            # Exclude already used problems

            if problem["id"] in exclude_ids:
                continue

            # Topic filter

            if (
                topic is not None
                and problem["topic"] != topic
            ):
                continue

            # Difficulty filter

            if (
                difficulty is not None
                and problem["difficulty"] != difficulty
            ):
                continue

            matches.append(problem)

        return matches