# Sudoku Solver  
  
Sudoku Solver written in Python.  
Written and tested on Python 3.13.  
  
# Usage  
  
Instantiate a `SudokuSolver` class with the given complexity N.  
For example, a standard 9x9 grid has a complexity `3`.  
The minimum supported is `2`, i.e. 4x4 grids.  
  
Then call the `solve` function by passing the grid to solve as a parameter.  
The grid must be a list of N⁴ integers, i.e. 81 for standard grids.  
Empty cells must contain `None`.  
Non-empty cells must contain **zero-indexed** value (meaning from 0 to 8 for standard grids).  
Check the example included:  
```python
if __name__ == "__main__":
    import time
    _ = None
    start = time.time()
    solution : Grid = SudokuSolver(3).solve([
        7, _, _, _, _, _, _, _, _,
        _, _, 2, 5, _, _, _, _, _,
        _, 6, _, _, 8, _, 1, _, _,
        _, 4, _, _, _, 6, _, _, _,
        _, _, _, _, 3, 4, 6, _, _,
        _, _, _, 0, _, _, _, 2, _,
        _, _, 0, _, _, _, _, 5, 7,
        _, _, 7, 4, _, _, _, 0, _,
        _, 8, _, _, _, _, 3, _, _,
    ])
    end = time.time()
    if solution is None:
        print("This grid has no solutions")
    else:
        print("Solution:")
        print(solution.to_string(repr=('1', '2', '3', '4', '5', '6', '7', '8', '9')))
    print("Ended in {:.2f}ms".format((end - start) * 1000))
```  
  
You can get a string representation of a grid, solved or not, using the `to_string` function.  
There is two optional keyword parameters available:  
- `repr`: A tuple of the characters to replace the numeric value with. The tuple must have a size of N². For example, for a standard grid, you might want to display the result with one indexed numbers, so you'll use `('1', '2', '3', '4', '5', '6', '7', '8', '9')`.  
- `rjust`: The width in number of characters for each cell. The default and minimum is 1.  