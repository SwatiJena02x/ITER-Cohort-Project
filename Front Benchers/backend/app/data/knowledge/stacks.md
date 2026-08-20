# Stacks

A stack is a Last-In-First-Out (LIFO) data structure. The last element added is the first one removed. In Python, a list can be used as a stack with `append()` (push) and `pop()` (pop).

## When to Use a Stack
- When you need to match or validate pairs (parentheses, brackets)
- When you need to track nested structures
- When you need to reverse the order of elements
- When you need to implement backtracking or undo operations
- When the problem involves "last opened must be first closed" logic

## Common Patterns
- **Bracket Matching (Valid Parentheses)**: Push opening brackets onto the stack. When you encounter a closing bracket, pop from the stack and check if it matches. If the stack is empty at the end, all brackets are matched.
- **Monotonic Stack**: Maintain a stack where elements are in increasing or decreasing order. Used for "next greater element" and similar problems.
- **Expression Evaluation**: Use a stack to evaluate postfix expressions or convert infix to postfix.

## Python Implementation
```python
stack = []           # empty stack
stack.append(item)   # push O(1)
top = stack.pop()    # pop O(1)
top = stack[-1]      # peek O(1)
if not stack:        # check empty
```

## Complexity
- Time: O(1) for push, pop, peek
- Space: O(n) in the worst case (all elements on the stack)

## Valid Parentheses Strategy
1. Create a mapping: closing bracket → matching opening bracket
2. For each character: if it's an opening bracket, push it. If it's a closing bracket, pop and check match.
3. Return True only if the stack is empty at the end.

## Common Mistakes
- Popping from an empty stack (always check `if stack` before popping)
- Using string replacement in a loop instead of a stack (O(n²) vs O(n))
- Forgetting to check if the stack is empty at the end (unmatched opening brackets)
