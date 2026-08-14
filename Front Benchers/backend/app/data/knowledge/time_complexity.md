# Time Complexity (Big-O)

Time complexity describes how the runtime of an algorithm scales with input size. It is expressed using Big-O notation, which captures the worst-case growth rate.

## Common Complexities (Best to Worst)

| Big-O | Name | Example |
|-------|------|---------|
| O(1) | Constant | Hash map lookup, array index access |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Single loop through array |
| O(n log n) | Linearithmic | Merge sort, efficient sorting |
| O(n²) | Quadratic | Nested loops over same array |
| O(2^n) | Exponential | Recursive fibonacci without memoization |

## Why O(n²) is Usually Bad
- Two nested for-loops both iterating over the input array gives O(n²)
- For an array of 10,000 elements, that's 100,000,000 operations
- Most problems with O(n²) brute force have an O(n) or O(n log n) optimal solution
- The key insight is usually: "can I avoid re-scanning by remembering what I've already seen?"

## How to Optimize from O(n²) to O(n)
- **Use a hash map or set**: Store seen elements for O(1) lookup instead of scanning the array again
- **Use two pointers**: If the array is sorted, use two pointers moving inward
- **Use a sliding window**: For subarray problems, maintain a window that expands and contracts
- **Precompute**: Build prefix sums or other precomputed structures

## Space-Time Tradeoff
- You can often trade extra space for faster time
- Example: Two Sum — O(n²) time O(1) space with brute force, or O(n) time O(n) space with a hash map
- The hash map approach is almost always preferred in interviews

## Common Mistakes
- Assuming nested loops are always bad (sometimes the inner loop runs a constant number of times)
- Using sorted() when a hash-based approach would be faster (O(n log n) vs O(n))
- Not considering space complexity alongside time complexity
