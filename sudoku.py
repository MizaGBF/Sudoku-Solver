from __future__ import annotations
from collections import deque

class Conflict(Exception):
    pass

class Cell:
    def __init__(self, block_size : int = 0, *, init_value : int = None):
        if init_value is not None:
            self.bits = init_value
        else:
            self.bits = (1 << (block_size*block_size)) - 1

    def eliminate(self, v : int, side_len : int) -> bool:
        if self.is_solved():
            if v == self.value(side_len):
                raise Conflict("Conflict while trying to unset solved value")
            return False
        self.bits = self.bits & ~(1 << v)
        return True
        
    def is_solved(self) -> bool:
        return (self.bits & (self.bits - 1)) == 0

    def assign(self, v : int) -> bool:
        if self.bits & (1 << v) == 0:
            return False
        self.bits = (1 << v)
        return True

    def value(self, side_len : int) -> int:
        if not self.is_solved():
            raise Exception("This cell isn't solved yet")
        for v in range(side_len):
            if self.bits & (1 << v) != 0:
                return v
        raise Exception("Unexpected code path")

    def count_candidates(self, side_len : int) -> int:
        if self.is_solved():
            return 0
        count = 0
        for v in range(side_len):
            if self.bits & (1 << v) != 0:
                count += 1
        return count

    def candidates(self, side_len : int) -> list[int]:
        if self.is_solved():
            return []
        return [v for v in range(side_len) if self.bits & (1 << v) != 0]

class Grid:
    def __init__(self, block_size : int, side_len : int, total_cells : int, *, grid : list[Cell] = None):
        self.block_size = block_size
        self.side_len = side_len
        self.total_cells = total_cells
        self._grid : list[Cell]
        if grid is None:
            self._grid = [Cell(block_size) for i in range(total_cells)]
        else:
            self._grid = [Cell(init_value=grid[i].bits) for i in range(total_cells)]

    def copy(self) -> Grid:
        return Grid(self.block_size, self.side_len, self.total_cells, grid=self._grid)

    def is_solved(self) -> bool:
        return len(self.get_unassigned()) == 0

    def get_cell_per_coords(self, x : int, y : int) -> Cell:
        return self._grid[x + self.side_len * y]

    def get_cell_per_index(self, index : int) -> Cell:
        return self._grid[index]

    def get_unassigned(self) -> list[int]:
        table : dict[int, int] = {}
        for p in range(self.total_cells):
            n : int = self._grid[p].count_candidates(self.side_len)
            if n > 0:
                table[p] = n
        return [key for key, value in sorted(table.items(), key=lambda item: item[1])]

    def assign(self, x : int, y : int, v : int) -> None:
        if not self._grid[x + self.side_len * y].assign(v):
            raise Exception(f"Cell ({x},{y}) is already assigned")
        queue = deque([(x, y, v)])
        self.propagate(queue)

    def propagate(self, queue : deque):
        # propagate
        while queue:
            x, y, v = queue.popleft()
            for p in self.peers(x, y):
                i = p % self.side_len
                j = p // self.side_len
                peer : Cell = self._grid[p]
                try:
                    if peer.eliminate(v, self.side_len):
                        if peer.is_solved():
                            queue.append((i, j, peer.value(self.side_len)))
                except Conflict:
                    raise Conflict(f"Conflict occured while eliminating value {v} for peer ({i},{j}) from cell ({x},{y})")
                except Exception as e:
                    raise e

    def peers(self, x : int, y : int):
        positions : set[int] = set()
        # square
        square = (x - x % self.block_size, y - y % self.block_size)
        for i in range(square[0], square[0] + self.block_size):
            for j in range(square[1], square[1] + self.block_size):
                if i != x or j != y:
                    positions.add(i + self.side_len * j)
        # column
        for i in range(self.side_len):
            if i != x:
                positions.add(i + self.side_len * y)
        # row
        for j in range(self.side_len):
            if j != y:
                positions.add(x + self.side_len * j)
        # yield possible positions
        for p in positions:
            yield p

    def to_string(self, *, repr : tuple[str]|None = None, rjust : int = 1) -> str:
        if isinstance(repr, tuple) and len(repr) != self.side_len:
            repr = None
        else:
            repr = None
        if rjust < 1:
            rjust = 1
        result = []
        for y in range(self.side_len):
            for x in range(self.side_len):
                p = x + self.side_len * y
                if self._grid[p].is_solved():
                    if repr is not None:
                        result.append(repr[self._grid[p].value(self.side_len)].rjust(rjust))
                    else:
                        result.append(str(self._grid[p].value(self.side_len)).rjust(rjust))
                else:
                    result.append("_" * rjust)
            result.append("\n")
        return "".join(result)

class SudokuSolver:
    def __init__(self, complexity : int):
        if complexity < 2:
            raise Exception("Complexity must be greater or equal to 2")
        self.block_size = complexity
        self.side_len = self.block_size * self.block_size
        self.total_cells = self.side_len * self.side_len

    def solve(self, grid : list[int|None]) -> Grid|None:
        if len(grid) != self.total_cells:
            raise Exception("Invalid grid size")
        # Initialize and populate grid
        g = Grid(self.block_size, self.side_len, self.total_cells)
        queue = deque()
        for p in range(self.total_cells):
            if grid[p] is not None:
                x : int = p % self.side_len
                y : int = p // self.side_len
                if grid[p] < 0 or grid[p] >= self.side_len:
                    raise Exception(f"Invalid grid cell value ({x},{y})")
                g.get_cell_per_index(p).assign(grid[p])
                queue.append((x, y, grid[p]))
        # Propagate initial assigments
        try:
            g.propagate(queue)
        except Conflict as c:
            print("Initial grid isn't valid:", c)
            return None
        except Exception as e:
            print("An exception occured:", e)
            return None
        
        stack : list[Grid] = [g]
        while len(stack) > 0:
            g = stack.pop()
            unassigneds : list[int] = g.get_unassigned()
            if len(unassigneds) == 0:
                return g
            cell : Cell = g.get_cell_per_index(unassigneds[0])
            x : int = unassigneds[0] % self.side_len
            y : int = unassigneds[0] // self.side_len
            for v in cell.candidates(self.side_len):
                try:
                    cpy = g.copy()
                    cpy.assign(x, y, v)
                    if cpy.is_solved():
                        return cpy
                    stack.append(cpy)
                except Conflict:
                    pass
        return None

if __name__ == "__main__":
    _ = None
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
    if solution is None:
        print("This grid has no solutions")
    else:
        print("Solution:")
        print(solution.to_string(repr=('1', '2', '3', '4', '5', '6', '7', '8', '9')))