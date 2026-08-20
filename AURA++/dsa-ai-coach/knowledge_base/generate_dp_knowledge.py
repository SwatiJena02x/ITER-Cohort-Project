from pathlib import Path


OUTPUT_DIR = Path(
    "knowledge_base/documents"
)


DP_TOPICS = {

    "dp_01_house_robber.txt": """
TITLE: House Robber

Problem Statement:
Given an array of integers where nums[i] represents the money in
the ith house, determine the maximum amount of money that can be
robbed without robbing two adjacent houses.

Core Idea:
At every house, choose between skipping the current house or robbing it.

DP State:
dp[i] = maximum money that can be robbed from houses 0..i.

Base Cases:
dp[0] = nums[0].
For the first two houses, dp[1] = max(nums[0], nums[1]).

Transition:
dp[i] = max(dp[i-1], dp[i-2] + nums[i]).

Algorithm:
Initialize the first one or two states and iterate through the array.

Example:
nums = [2, 7, 9, 3, 1]
Answer = 12.

Time Complexity:
O(n).

Space Complexity:
O(n), or O(1) with rolling variables.

Common Mistakes:
Using adjacent houses together or mishandling arrays of size 0 or 1.

Optimization:
Only the previous two DP states are required, so O(1) extra space is possible.

Key Takeaway:
House Robber is a classic choose-or-skip dynamic programming problem.
""",

    "dp_02_climbing_stairs.txt": """
TITLE: Climbing Stairs

Problem Statement:
There are n steps. At each move you can climb either 1 or 2 steps.
Return the number of distinct ways to reach the top.

Core Idea:
The number of ways to reach step i comes from step i-1 or step i-2.

DP State:
dp[i] = number of ways to reach step i.

Base Cases:
dp[0] = 1.
dp[1] = 1.

Transition:
dp[i] = dp[i-1] + dp[i-2].

Example:
n = 5
Answer = 8.

Time Complexity:
O(n).

Space Complexity:
O(n), or O(1) using two variables.

Common Mistakes:
Confusing number of ways with minimum number of steps.

Key Takeaway:
This problem follows the Fibonacci-style recurrence.
""",

    "dp_03_coin_change.txt": """
TITLE: Coin Change

Problem Statement:
Given coin denominations and a target amount, return the minimum
number of coins required to make that amount. Return -1 if impossible.

Core Idea:
Build the answer for smaller amounts and reuse them.

DP State:
dp[a] = minimum number of coins needed to make amount a.

Base Case:
dp[0] = 0.

Transition:
dp[a] = min(dp[a], dp[a-coin] + 1) for every usable coin.

Example:
coins = [1, 2, 5], amount = 11
Answer = 3 because 11 = 5 + 5 + 1.

Time Complexity:
O(amount * number_of_coins).

Space Complexity:
O(amount).

Common Mistakes:
Using an invalid initial value, ignoring unreachable amounts,
or using a greedy approach when greedy is not guaranteed to work.

Key Takeaway:
Coin Change is a bottom-up one-dimensional dynamic programming problem.
""",

    "dp_04_longest_increasing_subsequence.txt": """
TITLE: Longest Increasing Subsequence

Problem Statement:
Given an integer array, find the length of the longest strictly
increasing subsequence.

Core Idea:
For every element, determine the longest increasing subsequence
ending at that element.

DP State:
dp[i] = length of the longest increasing subsequence ending at i.

Base Case:
dp[i] = 1 for every i.

Transition:
If nums[j] < nums[i], then:
dp[i] = max(dp[i], dp[j] + 1).

Example:
nums = [10, 9, 2, 5, 3, 7, 101, 18]
Answer = 4.

Time Complexity:
O(n^2) for the basic DP solution.

Space Complexity:
O(n).

Optimization:
The problem can be solved in O(n log n) using patience sorting and binary search.

Key Takeaway:
Think about the subsequence ending at each index.
""",

    "dp_05_partition_equal_subset_sum.txt": """
TITLE: Partition Equal Subset Sum

Problem Statement:
Determine whether an array can be divided into two subsets having equal sums.

Core Idea:
The problem can be reduced to finding whether a subset with sum total/2 exists.

DP State:
dp[s] indicates whether sum s is achievable.

Base Case:
dp[0] = True.

Transition:
For each number, update achievable sums from right to left.

Example:
nums = [1, 5, 11, 5]
Answer = True because [1, 5, 5] and [11] have equal sum 11.

Time Complexity:
O(n * target), where target is total_sum / 2.

Space Complexity:
O(target).

Common Mistakes:
Forgetting that the total sum must be even or iterating sums in the wrong direction.

Key Takeaway:
This is a 0/1 subset-sum style dynamic programming problem.
""",

    "dp_06_0_1_knapsack.txt": """
TITLE: 0/1 Knapsack

Problem Statement:
Given items with weights and values and a capacity, maximize total value
without exceeding capacity. Each item can be used at most once.

Core Idea:
For each item, choose whether to take it or skip it.

DP State:
dp[w] = maximum value achievable with capacity w.

Transition:
dp[w] = max(dp[w], dp[w-weight] + value).

Time Complexity:
O(n * capacity).

Space Complexity:
O(capacity) with one-dimensional optimization.

Common Mistakes:
Processing capacities in the wrong direction when using a one-dimensional DP array.

Key Takeaway:
0/1 means each item is either selected once or not selected.
""",

    "dp_07_unbounded_knapsack.txt": """
TITLE: Unbounded Knapsack

Problem Statement:
Maximize value with a capacity when each item can be selected unlimited times.

Core Idea:
Unlike 0/1 Knapsack, an item can be reused.

DP State:
dp[w] = maximum value achievable for capacity w.

Transition:
dp[w] = max(dp[w], dp[w-weight] + value).

Time Complexity:
O(n * capacity).

Space Complexity:
O(capacity).

Key Difference:
In 0/1 Knapsack each item is used at most once.
In Unbounded Knapsack items may be reused.

Key Takeaway:
Loop direction matters when using a one-dimensional DP array.
""",

    "dp_08_house_robber_ii.txt": """
TITLE: House Robber II

Problem Statement:
Houses are arranged in a circle. Adjacent houses cannot both be robbed.

Core Idea:
Because the first and last houses are adjacent, solve two linear cases:
1. Exclude the first house.
2. Exclude the last house.

DP State:
Use the standard House Robber recurrence inside each linear range.

Example:
nums = [2, 3, 2]
Answer = 3.

Time Complexity:
O(n).

Space Complexity:
O(1) with rolling variables.

Common Mistakes:
Applying the ordinary House Robber recurrence directly to the circular array.

Key Takeaway:
Circular DP problems are often split into two linear cases.
""",

    "dp_09_decode_ways.txt": """
TITLE: Decode Ways

Problem Statement:
A digit string maps 1-26 to letters. Count the number of ways to decode it.

Core Idea:
At each position, consider using one digit or two valid digits.

DP State:
dp[i] = number of ways to decode the first i characters.

Base Case:
dp[0] = 1.

Transition:
Add dp[i-1] if the current digit is valid.
Add dp[i-2] if the two-digit number is between 10 and 26.

Time Complexity:
O(n).

Space Complexity:
O(n), or O(1) with rolling values.

Common Mistakes:
Incorrect handling of zeroes.

Key Takeaway:
Two possible transition lengths make this a useful string DP problem.
""",

    "dp_10_unique_paths.txt": """
TITLE: Unique Paths

Problem Statement:
Count the number of ways to move from the top-left to the bottom-right
of an m x n grid, moving only right or down.

Core Idea:
Each cell can be reached from the cell above or the cell to the left.

DP State:
dp[r][c] = number of ways to reach cell (r, c).

Base Case:
First row and first column each have one way.

Transition:
dp[r][c] = dp[r-1][c] + dp[r][c-1].

Time Complexity:
O(m*n).

Space Complexity:
O(m*n), or O(n) with rolling rows.

Key Takeaway:
Grid movement problems often have local predecessor transitions.
""",

    "dp_11_minimum_path_sum.txt": """
TITLE: Minimum Path Sum

Problem Statement:
Find the minimum sum path from the top-left to bottom-right of a grid,
moving only right or down.

Core Idea:
The minimum cost to reach a cell depends on the minimum cost of its
top and left predecessors.

DP State:
dp[r][c] = minimum path sum to reach cell (r, c).

Transition:
grid[r][c] + min(dp[r-1][c], dp[r][c-1]).

Time Complexity:
O(m*n).

Space Complexity:
O(m*n), or O(n) optimized.

Common Mistakes:
Handling first row, first column, and negative/large values incorrectly.

Key Takeaway:
Replace counting with minimizing when the objective is path cost.
""",

    "dp_12_word_break.txt": """
TITLE: Word Break

Problem Statement:
Determine whether a string can be segmented into dictionary words.

Core Idea:
Check whether a valid dictionary word can end at each position.

DP State:
dp[i] = whether the prefix of length i can be segmented.

Base Case:
dp[0] = True.

Transition:
dp[i] is true if there exists j < i such that dp[j] is true and
s[j:i] is in the dictionary.

Time Complexity:
Typically O(n^2) substring checks, depending on implementation.

Space Complexity:
O(n).

Common Mistakes:
Checking dictionary membership inefficiently or mishandling empty prefixes.

Key Takeaway:
Prefix-based state definitions work well for string segmentation.
""",

    "dp_13_longest_common_subsequence.txt": """
TITLE: Longest Common Subsequence

Problem Statement:
Given two strings, return the length of their longest common subsequence.

Core Idea:
Compare the current characters. If they match, extend the LCS.
Otherwise, discard one character from one of the strings.

DP State:
dp[i][j] = LCS length for prefixes of lengths i and j.

Transition:
If chars match: 1 + dp[i-1][j-1].
Otherwise: max(dp[i-1][j], dp[i][j-1]).

Time Complexity:
O(m*n).

Space Complexity:
O(m*n), or O(n) optimized.

Key Takeaway:
LCS is a classic two-dimensional string DP problem.
""",

    "dp_14_edit_distance.txt": """
TITLE: Edit Distance

Problem Statement:
Find the minimum number of insertions, deletions, and substitutions
needed to transform one string into another.

DP State:
dp[i][j] = minimum edits to transform the first i characters of
one string into the first j characters of the other.

Base Cases:
Transforming an empty string requires insertions or deletions.

Transition:
If characters match, use dp[i-1][j-1].
Otherwise use 1 + min(insert, delete, replace).

Time Complexity:
O(m*n).

Space Complexity:
O(m*n), or O(n).

Key Takeaway:
String transformation naturally maps to a two-dimensional DP state.
""",

    "dp_15_maximum_subarray.txt": """
TITLE: Maximum Subarray

Problem Statement:
Find the contiguous subarray with the largest sum.

Core Idea:
At each position, decide whether to extend the previous subarray
or start a new subarray.

DP State:
dp[i] = maximum subarray sum ending at i.

Transition:
dp[i] = max(nums[i], dp[i-1] + nums[i]).

Example:
nums = [-2,1,-3,4,-1,2,1,-5,4]
Answer = 6.

Time Complexity:
O(n).

Space Complexity:
O(1) with rolling values.

Key Takeaway:
This is commonly known as Kadane's algorithm.
""",

    "dp_16_target_sum.txt": """
TITLE: Target Sum

Problem Statement:
Assign + or - to each number so that the resulting sum equals target.
Count the number of valid assignments.

Core Idea:
This can be transformed into a subset-sum counting problem under
appropriate conditions.

DP State:
dp[s] = number of ways to achieve sum s.

Time Complexity:
Depends on the transformed subset-sum range.

Space Complexity:
Typically O(target-like range).

Common Mistakes:
Ignoring impossible parity conditions or mishandling zeros.

Key Takeaway:
Many sign-assignment problems can be transformed into subset-sum problems.
""",

    "dp_17_interleaving_string.txt": """
TITLE: Interleaving String

Problem Statement:
Determine whether a string s3 can be formed by interleaving s1 and s2
while preserving the relative order of characters in each string.

DP State:
dp[i][j] = whether the first i characters of s1 and first j characters
of s2 can form the first i+j characters of s3.

Transition:
Take the next character from s1 or s2 when it matches s3.

Time Complexity:
O(m*n).

Space Complexity:
O(m*n), or O(n).

Key Takeaway:
Use two indices to represent how much of each source string has been consumed.
""",

    "dp_18_distinct_subsequences.txt": """
TITLE: Distinct Subsequences

Problem Statement:
Count how many distinct subsequences of string s equal string t.

DP State:
dp[i][j] = number of ways to form the first j characters of t using
the first i characters of s.

Transition:
If characters match, include possibilities using or skipping s[i].
Otherwise skip the current character.

Time Complexity:
O(m*n).

Space Complexity:
O(m*n), or O(n) optimized.

Common Mistakes:
Confusing subsequences with substrings.

Key Takeaway:
The transition often branches into take or skip.
""",

    "dp_19_palindromic_substrings.txt": """
TITLE: Palindromic Substrings

Problem Statement:
Count the number of substrings that are palindromes.

Core Idea:
A substring is a palindrome if its end characters match and the inside
is also a palindrome.

DP State:
dp[i][j] = whether substring i..j is a palindrome.

Base Cases:
Length 1 substrings are palindromes.
Length 2 is a palindrome if both characters match.

Transition:
dp[i][j] = true if s[i] == s[j] and the inside is a palindrome.

Time Complexity:
O(n^2).

Space Complexity:
O(n^2) for the classic DP approach.

Key Takeaway:
Interval DP is useful when the state is defined by a left and right boundary.
""",

    "dp_20_matrix_chain_multiplication.txt": """
TITLE: Matrix Chain Multiplication

Problem Statement:
Given matrices, determine the minimum number of scalar multiplications
needed to multiply them.

Core Idea:
Choose the best place to split the chain.

DP State:
dp[i][j] = minimum multiplication cost for matrices i through j.

Base Case:
dp[i][i] = 0.

Transition:
Try every split k between i and j and choose the minimum cost.

Time Complexity:
O(n^3).

Space Complexity:
O(n^2).

Key Takeaway:
This is a classic interval DP problem where the transition tries every split.
"""
}


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    created = 0

    for filename, content in DP_TOPICS.items():

        path = OUTPUT_DIR / filename

        path.write_text(
            content.strip() + "\n",
            encoding="utf-8"
        )

        created += 1

        print(
            f"Created: {path}"
        )

    print()
    print(
        f"Created {created} DP knowledge documents."
    )


if __name__ == "__main__":
    main()