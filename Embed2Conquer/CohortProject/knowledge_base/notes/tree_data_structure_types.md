# Complete Reference: Types of Trees in Data Structures

A consolidated reference spanning GeeksforGeeks' structural classification, LeetCode's explicit tree types, and standard CS/interview vocabulary.

---

## A. By Number of Children (Core Structural Taxonomy)

| Type | Rule |
|---|---|
| **Binary Tree** | ≤2 children per node |
| **Ternary Tree** | ≤3 children per node |
| **N-ary Tree (Generic Tree)** | ≤N children per node |
| **Quad-Tree** | Exactly 4 children per internal node (topLeft, topRight, bottomLeft, bottomRight) |

---

## B. By Shape/Structure (Sub-types of Binary Tree)

| Type | Rule |
|---|---|
| **Full Binary Tree** | Every node has 0 or 2 children |
| **Complete Binary Tree** | All levels full except possibly the last, filled left→right |
| **Perfect Binary Tree** | All internal nodes have 2 children, all leaves at same depth |
| **Balanced Binary Tree** | Height difference ≤1 between left/right subtrees at every node |
| **Degenerate/Pathological Tree** | Every node has only one child |
| **Skewed Binary Tree** | A degenerate tree leaning entirely left or entirely right |

---

## C. By Value-Ordering Property

| Type | Rule |
|---|---|
| **Binary Search Tree (BST)** | Left subtree < node < right subtree |
| **Min-Heap** | Parent ≤ children (root = minimum) |
| **Max-Heap** | Parent ≥ children (root = maximum) |
| **Treap** | BST ordering by key + Heap ordering by a random priority, combined |
| **Cartesian Tree** | Binary tree satisfying heap property on values, BST property on array indices |

---

## D. Self-Balancing BST Variants

| Type | Balancing Mechanism |
|---|---|
| **AVL Tree** | Rotations based on strict height-balance factor (−1, 0, +1) |
| **Red-Black Tree** | Rotations + node coloring rules |
| **Splay Tree** | Recently-accessed nodes moved to root via splaying |
| **Treap** | Randomized balancing (also fits under value-ordering) |
| **Weight-Balanced Tree** | Balance based on subtree sizes rather than height |

---

## E. Specialized / Advanced Tree ADTs

| Type | Purpose |
|---|---|
| **Segment Tree** | Range queries (sum/min/max) with updates |
| **Binary Indexed Tree (Fenwick Tree)** | Prefix sums, point updates, lighter than Segment Tree |
| **Trie (Prefix Tree)** | Prefix-based string storage/search |
| **Ternary Search Tree** | Trie with BST-ordered children, saves space vs. array-based trie |
| **Suffix Tree** | All suffixes of a string, for fast substring search |
| **Suffix Array + LCP Tree** | Array-based alternative to suffix trees |
| **B-Tree** | Self-balancing multi-way tree for disk-based indexing |
| **B+ Tree** | B-Tree variant storing data only at leaves, used in databases |
| **Interval Tree** | Stores intervals, queries overlapping ranges |
| **k-d Tree** | Multi-dimensional BST, used for nearest-neighbor/spatial search |
| **R-Tree** | Spatial indexing for rectangles/bounding boxes (maps, GIS) |
| **Van Emde Boas Tree** | Integer key operations in O(log log n) |

---

## F. Application-Specific Trees

| Type | Used For |
|---|---|
| **Expression Tree** | Represents arithmetic/logical expressions (operators as internal nodes) |
| **Huffman Tree** | Optimal prefix codes for data compression |
| **Parse Tree / Syntax Tree** | Represents grammar structure in compilers |
| **Decision Tree** | Represents decision rules (machine learning) |
| **Spanning Tree** | Subgraph connecting all vertices of a graph with no cycles (graph theory, tree-derived) |
| **DOM Tree** | Represents HTML/XML document structure |
| **Game Tree** | Represents possible moves in games (minimax, alpha-beta pruning) |

---

## G. Forest Structures (Multiple Trees, Not One)

| Type | Rule |
|---|---|
| **Disjoint Set Forest (Union-Find)** | Collection of trees representing disjoint sets, each with a representative root |

---

## H. Explicit LeetCode Node Types

| Type | Node Definition Given |
|---|---|
| **N-ary Tree Node** | `{val, children: List<Node>}` |
| **Quad-Tree Node** | `{val, isLeaf, topLeft, topRight, bottomLeft, bottomRight}` |

---

## Quick-Reference Hierarchy

```
Tree Types
├── A. By children count: Binary, Ternary, N-ary, Quad-Tree
├── B. By shape: Full, Complete, Perfect, Balanced, Degenerate, Skewed
├── C. By value ordering: BST, Min-Heap, Max-Heap, Treap, Cartesian Tree
├── D. Self-balancing BSTs: AVL, Red-Black, Splay, Treap, Weight-Balanced
├── E. Advanced ADTs: Segment Tree, BIT/Fenwick, Trie, Ternary Search Tree,
│                     Suffix Tree, B-Tree, B+ Tree, Interval Tree, k-d Tree,
│                     R-Tree, Van Emde Boas Tree
├── F. Application-specific: Expression, Huffman, Parse/Syntax, Decision,
│                            Spanning, DOM, Game Tree
├── G. Forests: Disjoint Set Forest (Union-Find)
└── H. LeetCode explicit types: N-ary Tree Node, Quad-Tree Node
```

---

*Compiled from GeeksforGeeks' structural taxonomy, LeetCode problem definitions, and standard CS/interview reference material.*
