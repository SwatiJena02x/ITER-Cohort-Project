# Common Mistakes in DSA Problems

## Brute Force Trap
- The most common mistake is using nested loops when a single pass with a hash map/set would work
- Two nested for-loops over the same array is almost always a sign of O(n²) brute force
- Ask yourself: "Can I avoid the inner loop by remembering what I've already seen?"

## Off-by-One Errors
- Using `range(len(nums))` vs `range(len(nums) - 1)` — off by one in loop bounds
- Forgetting that Python's `range()` is exclusive on the upper bound
- Accessing `nums[i+1]` without checking if `i+1 < len(nums)`

## Wrong Data Structure Choice
- Using a list for lookups when a set or dict would give O(1) instead of O(n)
- Using sorted() when counting would be more efficient
- Not using a stack for problems that require LIFO ordering

## Type Errors
- Calling `len()` on an integer instead of a list or string
- Trying to iterate over a non-iterable
- Comparing incompatible types

## Incomplete Solutions
- Forgetting to handle edge cases (empty array, single element, all same elements)
- Not returning a value from the function
- Returning the wrong type (e.g., returning True/False instead of indices)

## Variable Naming
- Using single-letter variables that make code unreadable
- Shadowing built-in names (e.g., naming a variable `list` or `dict`)
- Using misleading names (e.g., using `nums` for a target value)

## Efficiency Mistakes
- Creating unnecessary copies of data structures
- Using string concatenation in a loop instead of `.join()`
- Sorting when you don't need to (O(n log n) when O(n) is possible)
