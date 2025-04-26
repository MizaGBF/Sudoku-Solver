from __future__ import annotations
from collections import deque

class Conflict(Exception):
    pass

class Grid:
    def __init__(
        self, block_size : int, side_len : int, total_cells : int,
        *,
        grid : list[int] = None,
        peer_cache : dict[int, set[int]]|None = None,
    ):
        self.peer_cache : dict[int, set[int]] = {} if peer_cache is None else peer_cache
        self.block_size = block_size
        self.side_len = side_len
        self.total_cells = total_cells
        self.grid : list[int] # the grid switched from the Cell instances from the previous version to pure integer, for performance
        if grid is None:
            self.grid = [((1 << (self.side_len)) - 1) for i in range(total_cells)] # we init each cell to an integer to N bits, raised to 1
        else:
            self.grid = grid

    def get_first_lowest_unassigned(self) -> int|None: # we look for the next unassigned cell with the LESS possible assignable values
        best : int = self.total_cells + 1
        index : int|None = None
        for p in range(self.total_cells):
            n : int = 0 if ((self.grid[p] & (self.grid[p] - 1)) == 0) else self.grid[p].bit_count() # number of raised bit if non solved
            if n == 2:
                return p
            elif 0 < n < best:
                best = n
                index = p
        return index

    def propagate(self, queue : deque):
        # propagate
        while queue:
            p, v = queue.popleft() # pop next element
            for q in self.peers(p):
                peer : int = self.grid[q]
                try:
                    if (peer & (peer - 1)) == 0: # is solved?
                        if v == peer.bit_length() - 1: # compare value with setter
                            raise Conflict("Conflict while trying to unset solved value")
                    else:
                        peer = peer & ~(1 << v) # lower down bit
                        self.grid[q] = peer # update grid
                        if (peer & (peer - 1)) == 0: # is solved
                            queue.append((q, peer))
                except Conflict:
                    raise Conflict(f"Conflict occured while eliminating value {v} for peer ({q % self.side_len},{q // self.side_len}) from cell ({p % self.side_len},{p // self.side_len})")
                except Exception as e:
                    raise e

    def peers(self, p : int) -> list[int]: # retrieve other cells which interact with our own
        positions : set[int]
        if p not in self.peer_cache: # we use cached values if it exists
            positions : set[int] = set() # list of peer's indexes
            # block
            block_start = ((p - p % self.block_size) % self.side_len) + p - (p % (self.side_len * self.block_size)) # top left corner of the block
            for x in range(0, self.block_size):
                for y in range(0, self.side_len * 3, self.side_len):
                    q : int = block_start + x + y
                    if q != p:
                        positions.add(q)
            # column
            y = (p // self.side_len) * self.side_len
            for x in range(0, self.side_len):
                q : int = x + y
                if q != p:
                    positions.add(q)
            # row
            x = p % self.side_len
            for y in range(0, self.total_cells, self.side_len):
                q : int = x + y
                if q != p:
                    positions.add(q)
            # set in cache
            self.peer_cache[p] = positions
        return self.peer_cache[p]

    def to_string(self, *, repr : tuple[str]|None = None, rjust : int = 1) -> str:
        # pretty print the grid
        # first, verify parameters
        if isinstance(repr, tuple) and len(repr) != self.side_len:
            repr = None
        else:
            repr = None
        if rjust < 1:
            rjust = 1
        # result will contain the output
        # we use a list with join to avoid ton of reallocations
        result = []
        for p in range(self.total_cells): # iterate over cells
            if p > 0 and p % self.side_len == 0: # add new line
                result.append("\n")
            if (self.grid[p] & (self.grid[p] - 1)) == 0: # is solved?
                # then print value or representation
                if repr is not None:
                    result.append(repr[self.grid[p].bit_length() - 1].rjust(rjust))
                else:
                    result.append(str(self.grid[p].bit_length() - 1).rjust(rjust))
            else:
                # else an underscore
                result.append("_" * rjust)
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
                if grid[p] < 0 or grid[p] >= self.side_len:
                    raise Exception(f"Invalid grid cell value ({p % self.side_len},{p // self.side_len})")
                g.grid[p] = (1 << grid[p])
                queue.append((p, grid[p]))
        # Propagate initial assigments
        try:
            g.propagate(queue)
        except Conflict as c:
            print("Initial grid isn't valid:", c)
            return None
        stack : deque[Grid] = deque([g])
        while len(stack) > 0:
            g = stack.pop()
            unassigned : int|None = g.get_first_lowest_unassigned()
            if unassigned is None:
                return g
            cell : int = g.grid[unassigned]
            canditates : list[int] = [] if (cell & (cell - 1)) == 0 else [v for v in range(self.side_len) if cell & (1 << v) != 0]
            for v in canditates:
                try:
                    cpy = Grid(g.block_size, g.side_len, g.total_cells, grid=g.grid.copy(), peer_cache=g.peer_cache) # create a copy
                    # assign value to cell
                    if cpy.grid[unassigned] & (1 << v) == 0: # is solved?
                        return Exception(f"Cell ({unassigned % self.side_len},{unassigned // self.side_len}) is already assigned")
                    cpy.grid[unassigned] = (1 << v) # set only this bit raised
                    # propagate to other cells
                    queue.clear() # reuse existing queue
                    queue.append((unassigned, v))
                    cpy.propagate(queue)
                    stack.append(cpy)
                except Conflict:
                    pass
        return None

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