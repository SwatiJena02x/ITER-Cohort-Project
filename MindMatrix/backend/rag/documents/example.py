# Two Sum example
# Uses a hash map for O(n) lookup


def two_sum(nums, target):
    """
    Find two numbers that add up to target.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """

    # Dictionary stores numbers already visited
    seen = {}

    for i, num in enumerate(nums):

        # Calculate required value
        complement = target - num

        # Check whether complement exists
        if complement in seen:
            return [seen[complement], i]

        seen[num] = i

    return []