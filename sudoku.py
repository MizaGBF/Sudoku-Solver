from __future__ import annotations
from collections import deque

# Functions to avoid attribute lookup
_bcount_ = int.bit_count
_blen_ = int.bit_length
_deqclr_ = deque.clear
_deqapp_ = deque.append
_lstsrt_ = list.sort
_lstcpy_ = list.copy
_setadd_ = set.add
_setrem_ = set.remove

class Conflict(Exception):
    pass

class SudokuSolver:
    def __init__(self, complexity : int):
        if complexity < 2:
            raise Exception("Complexity must be greater or equal to 2")
        self.block_size : int = complexity # block of a sudoku grid (3 for standard one)
        self.side_len : int = self.block_size * self.block_size # length of a sudoku grid (9 for standard one). Is also the number of possible values
        self.total_cells : int = self.side_len * self.side_len # total number of cells
        # used in some calculs
        self.tri_side_len : int = self.side_len * 3 # 3 times the length of a sudoku grid
        self.block_x_side : int = self.block_size * self.side_len
        # for caching
        self.peers : list[set[int]|None] = [self.compute_peers(i) for i in range(self.total_cells)] # cache peer cell positions
        self.occurences : list[int] = [] # store occurences of each numbers (is reset with each solve call)

    def solve(self, input_grid : list[int|None]) -> list[int]|None:
        # Check if the input grid has the right size
        if len(input_grid) != self.total_cells:
            raise Exception("Invalid grid size")
        self.occurences = [0 for i in range(self.side_len)]
        # Initialize and populate grid
        g = [(((1 << (self.side_len)) - 1) if v is None else (1 << v)) for p, v in enumerate(input_grid)] # first grid
        # Note: each cell contains an integer with N number of bits raised (9 for a standard grid). A bit raised means the value can be assigned
        queue : deque[tuple[int, int]] = deque()
        for p, v in enumerate(g):
            if (v & (v - 1)) == 0:
                b : int = _blen_(v) - 1
                self.occurences[b] += 1
                _deqapp_(queue, (p, b)) # add to queue for propagation
        # Now propagate initial assigments
        try:
            self.propagate(g, queue)
        except Conflict as c:
            print("Initial grid isn't valid:", c)
            return None
        # Now try to fill the rest of the grid
        stack : deque[list[int]] = deque([g]) # the stack starts with our first grid
        while len(stack) > 0:
            g = stack.pop() # get top of stack
            unassigned : int|None = self.get_first_lowest_unassigned(g) # retrieve unsolved cell with less amount of possible values
            if unassigned is None: # no unassigned means the grid is solved
                return g
            cell : int = g[unassigned]
            # List the possible values
            canditates : list[int] = [] if (cell & (cell - 1)) == 0 else [v for v in range(self.side_len) if cell & (1 << v) != 0]
            # Sort by reverse occurences (i.e. Most populated ones first)
            _lstsrt_(canditates, key=lambda x: self.occurences[x], reverse=True)
            for v in canditates: # For each possible value
                try:
                    cpy = _lstcpy_(g) # create a copy of our grid
                    cpy[unassigned] = (1 << v) # set only this bit raised
                    # propagate to other cells
                    _deqclr_(queue) # reuse existing queue
                    _deqapp_(queue, (unassigned, v))
                    self.propagate(cpy, queue)
                    # No exception, we had our new grid to the stack
                    _deqapp_(stack, cpy)
                except Conflict:
                    pass
        return None

    def get_first_lowest_unassigned(self, grid : list[int]) -> int|None: # we look for the next unassigned cell with the LESS possible assignable values
        best : int = self.total_cells + 1
        index : int|None = None
        for p, v in enumerate(grid):
            n : int = _bcount_(v) # number of raised bit
            if n == 2: # minimum number for non solved cell
                return p
            elif n <= 1: # already solved
                continue
            elif n < best:
                best, index = n, p
        return index

    def propagate(self, grid : list[int], queue : deque):
        # propagate
        while queue:
            p, v = queue.popleft() # pop next element
            for q in self.peers[p]:
                peer : int = grid[q]
                prvl : int = _blen_(peer) - 1
                try:
                    if (peer & (peer - 1)) == 0: # is solved?
                        if v == prvl: # compare value with setter
                            raise Conflict("Conflict while trying to unset solved value")
                    else:
                        peer = peer & ~(1 << v) # lower down bit
                        grid[q] = peer # update grid
                        if (peer & (peer - 1)) == 0: # is solved
                            prvl = _blen_(peer) - 1
                            self.occurences[prvl] += 1
                            _deqapp_(queue, (q, prvl))
                except Conflict:
                    raise Conflict(f"Conflict occured while eliminating value {v} for peer ({q % self.side_len},{q // self.side_len}) from cell ({p % self.side_len},{p // self.side_len})")
                except Exception as e:
                    raise e

    def compute_peers(self, p : int) -> set[int]: # cache other cells which interact with our own
        positions : set[int] = set() # list of peer's indexes
        # block
        block_start = ((p - p % self.block_size) % self.side_len) + p - (p % self.block_x_side) # top left corner of the block
        for x in range(0, self.block_size):
            for y in range(0, self.tri_side_len, self.side_len):
                q : int = block_start + x + y
                _setadd_(positions, q)
        # column
        y = (p // self.side_len) * self.side_len
        for x in range(0, self.side_len):
            q : int = x + y
            _setadd_(positions, q)
        # row
        x = p % self.side_len
        for y in range(0, self.total_cells, self.side_len):
            q : int = x + y
            _setadd_(positions, q)
        _setrem_(positions, p)
        return positions

    def to_string(self, grid : list[int], *, repr : tuple[str]|None = None, rjust : int = 1) -> str:
        # pretty print the grid
        # first, verify parameters
        if isinstance(repr, tuple):
            if len(repr) != self.side_len:
                repr = None
        else:
            repr = None
        if rjust < 1:
            rjust = 1
        # result will contain the output
        # we use a list with join to avoid ton of reallocations
        result = []
        for p, v in enumerate(grid): # iterate over cells
            if p > 0 and p % self.side_len == 0: # add new line
                result.append("\n")
            if (v & (v - 1)) == 0: # is solved?
                # then print value or representation
                if repr is not None:
                    result.append(repr[_blen_(v) - 1].rjust(rjust))
                else:
                    result.append(str(_blen_(v) - 1).rjust(rjust))
            else:
                # else an underscore
                result.append("_" * rjust)
        return "".join(result)

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