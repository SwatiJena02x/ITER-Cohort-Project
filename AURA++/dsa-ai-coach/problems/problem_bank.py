# problems/problem_bank.py


PROBLEMS = [

    # ==========================================================
    # DYNAMIC PROGRAMMING
    # ==========================================================

    {
        "id": "dp_001",
        "title": "House Robber",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "You are given an integer array nums representing "
            "the amount of money in each house. You cannot rob "
            "two adjacent houses. Return the maximum amount of "
            "money you can rob."
        ),
        "hints": [
            "At every house, decide whether to rob it or skip it.",
            "If you rob the current house, you cannot rob the previous house.",
            "Define dp[i] as the maximum money that can be robbed from houses 0 through i."
        ]
    },

    {
        "id": "dp_002",
        "title": "Climbing Stairs",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "You are climbing a staircase. It takes n steps to "
            "reach the top. Each time you can either climb 1 or "
            "2 steps. Return the number of distinct ways you can "
            "climb to the top."
        ),
        "hints": [
            "Think about the possible steps from which you can reach the current step.",
            "You can reach step i from either step i-1 or step i-2.",
            "Define dp[i] as the number of ways to reach step i and combine the two previous states."
        ]
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
            "Return the fewest number of coins needed to make "
            "that amount. If the amount cannot be made up, "
            "return -1."
        ),
        "hints": [
            "Think about solving smaller amounts before solving the target amount.",
            "Define dp[x] as the minimum number of coins needed to make amount x.",
            "For every coin, consider dp[x - coin] + 1 and take the minimum valid value."
        ]
    },

    {
        "id": "dp_004",
        "title": "Longest Increasing Subsequence",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "Given an integer array nums, return the length of "
            "the longest strictly increasing subsequence."
        ),
        "hints": [
            "Think about the longest increasing subsequence that ends at each element.",
            "For every nums[i], look at previous elements nums[j] that are smaller than nums[i].",
            "Define dp[i] as the LIS length ending at i and use dp[j] + 1 whenever nums[j] < nums[i]."
        ]
    },

    {
        "id": "dp_005",
        "title": "Partition Equal Subset Sum",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "Given an integer array nums, return true if you can "
            "partition the array into two subsets such that the "
            "sum of the elements in both subsets is equal."
        ),
        "hints": [
            "First calculate the total sum of all elements.",
            "If the total sum is odd, can it be divided into two equal integer sums?",
            "If the sum is even, reduce the problem to finding whether a subset with sum total/2 exists."
        ]
    },

    {
        "id": "dp_006",
        "title": "0/1 Knapsack",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "Given weights and values of n items and a knapsack "
            "capacity, maximize the total value without exceeding "
            "the capacity. Each item can be selected at most once."
        ),
        "hints": [
            "For every item, you have two choices: take it or skip it.",
            "Think about the best value achievable for every possible capacity.",
            "Define dp[w] as the maximum value for capacity w and update capacities from right to left."
        ]
    },

    {
        "id": "dp_007",
        "title": "Unbounded Knapsack",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "Given weights and values of items and a capacity, "
            "maximize the total value when each item can be used "
            "an unlimited number of times."
        ),
        "hints": [
            "Unlike 0/1 Knapsack, an item can be selected more than once.",
            "Define dp[w] as the best value achievable with capacity w.",
            "Consider dp[w - weight] + value and allow the same item to be reused."
        ]
    },

    {
        "id": "dp_008",
        "title": "House Robber II",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "You are given houses arranged in a circle. You cannot "
            "rob two adjacent houses. Return the maximum amount "
            "of money you can rob."
        ),
        "hints": [
            "The first and last houses are adjacent because the houses form a circle.",
            "Consider two cases: exclude the first house or exclude the last house.",
            "Run the normal House Robber solution on both ranges and take the maximum."
        ]
    },

    {
        "id": "dp_009",
        "title": "Decode Ways",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "A message containing letters can be encoded using "
            "numbers from 1 to 26. Given a digit string, return "
            "the number of ways to decode it."
        ),
        "hints": [
            "At each position, check whether the current digit can form a valid one-digit code.",
            "Also check whether the current and previous digits form a number from 10 to 26.",
            "Define dp[i] as the number of ways to decode the first i characters."
        ]
    },

    {
        "id": "dp_010",
        "title": "Unique Paths",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "There is an m x n grid. Starting from the top-left "
            "corner, return the number of possible paths to reach "
            "the bottom-right corner when you can only move right "
            "or down."
        ),
        "hints": [
            "A cell can only be reached from the cell above or the cell to its left.",
            "Think about the number of ways to reach every cell.",
            "Define dp[r][c] as the number of paths to that cell and add the top and left states."
        ]
    },

    {
        "id": "dp_011",
        "title": "Minimum Path Sum",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "Given a grid filled with non-negative numbers, find "
            "a path from the top-left to bottom-right that minimizes "
            "the sum of all numbers along the path. You can only "
            "move right or down."
        ),
        "hints": [
            "Think about the minimum cost required to reach each cell.",
            "The previous cells that can lead to a cell are the one above and the one to the left.",
            "Define dp[r][c] as the minimum path sum and add the current value to the smaller predecessor."
        ]
    },

    {
        "id": "dp_012",
        "title": "Word Break",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "Given a string s and a dictionary of words, determine "
            "if s can be segmented into a space-separated sequence "
            "of one or more dictionary words."
        ),
        "hints": [
            "Think about whether prefixes of the string can already be formed using dictionary words.",
            "For every position i, try an earlier position j and check whether s[j:i] is a dictionary word.",
            "Define dp[i] as whether the first i characters can be segmented."
        ]
    },

    {
        "id": "dp_013",
        "title": "Longest Common Subsequence",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "Given two strings text1 and text2, return the length "
            "of their longest common subsequence."
        ),
        "hints": [
            "Compare characters from the two strings.",
            "If the characters match, they can contribute to the subsequence; otherwise consider skipping one character.",
            "Define dp[i][j] as the LCS length of the first i and first j characters."
        ]
    },

    {
        "id": "dp_014",
        "title": "Edit Distance",
        "topic": "dynamic_programming",
        "difficulty": "hard",
        "description": (
            "Given two strings word1 and word2, return the minimum "
            "number of operations required to convert word1 into "
            "word2. Allowed operations are insertion, deletion, "
            "and replacement."
        ),
        "hints": [
            "Think about the three operations: insert, delete, and replace.",
            "Define the problem using prefixes of the two strings.",
            "If characters differ, use 1 + min(insert, delete, replace); if they match, use the diagonal state."
        ]
    },

    {
        "id": "dp_015",
        "title": "Maximum Subarray",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "Given an integer array nums, find the contiguous "
            "subarray with the largest sum and return its sum."
        ),
        "hints": [
            "At each element, decide whether to continue the previous subarray or start a new one.",
            "The previous best subarray ending at the previous position is the state you need.",
            "Define dp[i] as the maximum subarray sum ending at i: max(nums[i], dp[i-1] + nums[i])."
        ]
    },

    {
        "id": "dp_016",
        "title": "Target Sum",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "Given an integer array nums and an integer target, "
            "assign either + or - to every element so that the "
            "resulting expression equals target. Return the number "
            "of different expressions."
        ),
        "hints": [
            "Each number can receive either a plus or minus sign.",
            "Try transforming the sign-assignment problem into a subset-sum problem.",
            "Let the positive subset have sum P and negative subset have sum N, then use P - N = target and P + N = total."
        ]
    },

    {
        "id": "dp_017",
        "title": "Interleaving String",
        "topic": "dynamic_programming",
        "difficulty": "hard",
        "description": (
            "Given strings s1, s2, and s3, determine whether s3 "
            "is formed by an interleaving of s1 and s2 while "
            "preserving the order of characters in each string."
        ),
        "hints": [
            "Track how many characters have been consumed from each source string.",
            "If i characters come from s1 and j from s2, then i+j characters have been consumed from s3.",
            "Define dp[i][j] as whether those prefixes can form the corresponding prefix of s3."
        ]
    },

    {
        "id": "dp_018",
        "title": "Distinct Subsequences",
        "topic": "dynamic_programming",
        "difficulty": "hard",
        "description": (
            "Given strings s and t, return the number of distinct "
            "subsequences of s which equals t."
        ),
        "hints": [
            "You need to count different ways to form t from s while preserving order.",
            "When characters match, consider both using the current character and skipping it.",
            "Define dp[i][j] as the number of ways to form the first j characters of t using the first i characters of s."
        ]
    },

    {
        "id": "dp_019",
        "title": "Palindromic Substrings",
        "topic": "dynamic_programming",
        "difficulty": "medium",
        "description": (
            "Given a string s, return the number of palindromic "
            "substrings in it."
        ),
        "hints": [
            "A palindrome depends on its two boundary characters.",
            "A substring of length 1 is always a palindrome, and a length-2 substring is a palindrome when both characters match.",
            "For longer substrings, check s[i] == s[j] and whether the inside substring is already a palindrome."
        ]
    },

    {
        "id": "dp_020",
        "title": "Matrix Chain Multiplication",
        "topic": "dynamic_programming",
        "difficulty": "hard",
        "description": (
            "Given a sequence of matrices, determine the minimum "
            "number of scalar multiplications needed to multiply "
            "the entire matrix chain."
        ),
        "hints": [
            "The key decision is where to split the matrix chain.",
            "For matrices from i to j, try every possible split point k.",
            "Define dp[i][j] as the minimum multiplication cost for matrices i through j and choose the best split."
        ]
    },


    # ==========================================================
    # ARRAYS
    # ==========================================================

    {
        "id": "arr_001",
        "title": "Two Sum",
        "topic": "arrays",
        "difficulty": "easy",
        "description": (
            "Given an array of integers nums and an integer target, "
            "return indices of the two numbers such that they add "
            "up to target."
        ),
        "hints": [
            "Think about what value you need to find for each number.",
            "A hash map can store values you have already seen.",
            "For nums[i], check whether target - nums[i] already exists in the hash map."
        ]
    },

    {
        "id": "arr_002",
        "title": "Product of Array Except Self",
        "topic": "arrays",
        "difficulty": "medium",
        "description": (
            "Given an integer array nums, return an array answer "
            "such that answer[i] is equal to the product of all "
            "elements of nums except nums[i]. You must solve it "
            "without using division."
        ),
        "hints": [
            "For every position, think about the product of elements to its left and right.",
            "You can calculate prefix products first.",
            "Use a prefix product pass and a suffix product pass to construct the result."
        ]
    },


    # ==========================================================
    # STRINGS
    # ==========================================================

    {
        "id": "str_001",
        "title": "Longest Substring Without Repeating Characters",
        "topic": "strings",
        "difficulty": "medium",
        "description": (
            "Given a string s, find the length of the longest "
            "substring without repeating characters."
        ),
        "hints": [
            "Think about maintaining a window containing unique characters.",
            "Use two pointers to represent the current window.",
            "When a duplicate appears, move the left pointer until the window becomes valid again."
        ]
    },

    {
        "id": "str_002",
        "title": "Valid Anagram",
        "topic": "strings",
        "difficulty": "easy",
        "description": (
            "Given two strings s and t, return true if t is an "
            "anagram of s, and false otherwise."
        ),
        "hints": [
            "Two strings that are anagrams contain the same characters with the same frequencies.",
            "Think about counting the frequency of every character.",
            "Compare the character-frequency maps of the two strings."
        ]
    }
]