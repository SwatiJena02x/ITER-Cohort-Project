def house_robber(nums):
    """
    Return the maximum amount of money that can be robbed
    without robbing two adjacent houses.
    """

    if not nums:
        return 0

    if len(nums) == 1:
        return nums[0]

    prev_two = 0
    prev_one = 0

    for money in nums:
        current = max(
            prev_one,
            prev_two + money
        )

        prev_two = prev_one
        prev_one = current

    return prev_one