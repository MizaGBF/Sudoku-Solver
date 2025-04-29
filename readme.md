# Sudoku Solver  
  
Sudoku Solver written in Python.  
Written and tested on Python 3.13.  
A port written in C++17 is available in the `cpp` folder.  
  
## Note
  
This is merely a fun saturday-afternoon project.  
I tried to optimize it as much as possible for speed.  
Do note it assumes the grid passed to `solve` is valid (i.e. not containing negative values or values greater or equal to N²), make sure to check beforehand.  
  
## Usage  
  
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
    solver = SudokuSolver(3)
    start = time.time()
    solution : list[int] = solver.solve([
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
        print(solver.to_string(solution, repr=('1', '2', '3', '4', '5', '6', '7', '8', '9')))
    print("Ended in {:.2f}ms".format((end - start) * 1000))
```  
  
You can get a string representation of a grid, solved or not, using the `to_string` function.  
There is two optional keyword parameters available:  
- `repr`: A tuple of the characters to replace the numeric value with. The tuple must have a size of N². For example, for a standard grid, you might want to display the result with one indexed numbers, so you'll use `('1', '2', '3', '4', '5', '6', '7', '8', '9')`.  
- `rjust`: The width in number of characters for each cell. The default and minimum is 1.  
  
# CPP Version  
  
## Note  
  
This version requires a GCC/Clang compiler, C++17 compliant.  
  
This implementation is around 2.05 times faster than in Python but is limited to the size of `std::size_t` on your system.  
Meaning you can't instantiate `SudokuSolver<N>()` where N² is greated than the number of bits in `std::size_t` (i.e 8 if size_t is 64 bits long).  
This can be solved by changing the definition of `myuint` in `sudoku.hpp` and likely by changing the use of `__builtin_clzll` to the appropriate function.  
  
## Usage  
  
Refer to the `main.cpp` file to have an example of how to use it.  
If the grid is unsolvable, it will return an empty grid.  
  
For building, uses cmake.  
For example, on Windows with MinGW:  
```
cmake -B build -G "MinGW Makefiles"
cd build
make
cd ..
```  
Make sure your compiler and its libraries are in your PATH.  