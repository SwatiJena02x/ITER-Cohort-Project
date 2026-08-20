from tools import CodeAnalysisTool


def main():

    print("\n" + "=" * 60)
    print("CODE ANALYSIS TOOL TEST")
    print("=" * 60)

    tool = CodeAnalysisTool()

    problem = """
You are given an array nums representing money
in houses. You cannot rob two adjacent houses.
Return the maximum amount of money you can rob.
"""

    code = """
def rob(nums):

    n = len(nums)

    dp = [0] * n

    dp[0] = nums[0]

    for i in range(1, n):

        for j in range(i - 1):

            dp[i] = max(
                dp[i],
                dp[j] + nums[i]
            )

    return dp[n - 1]
"""

    print("\nAnalyzing code...\n")

    result = tool.execute(
        code=code,
        problem=problem
    )

    print(result)


if __name__ == "__main__":
    main()