#include "sudoku.hpp"
#include <chrono>

int main()
{
	const std::vector<size_t> input = {
		8, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 3, 6, 0, 0, 0, 0, 0,
		0, 7, 0, 0, 9, 0, 2, 0, 0,
		0, 5, 0, 0, 0, 7, 0, 0, 0,
		0, 0, 0, 0, 4, 5, 7, 0, 0,
		0, 0, 0, 1, 0, 0, 0, 3, 0,
		0, 0, 1, 0, 0, 0, 0, 6, 8,
		0, 0, 8, 5, 0, 0, 0, 1, 0,
		0, 9, 0, 0, 0, 0, 4, 0, 0
	};
	
	auto solver = SudokuSolver<3>();
	auto start = std::chrono::high_resolution_clock::now();
	const auto grid = solver.solve(input);
	auto end = std::chrono::high_resolution_clock::now();
	
	if(grid)
		solver.print(grid.value());
	else
		std::cout << "No solutions for given grid" << std::endl;
	std::cout << "Done in " << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count() << "us" << std::endl;
	return 0;
}