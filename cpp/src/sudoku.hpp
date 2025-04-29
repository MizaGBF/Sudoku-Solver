#ifndef __SUDOKU__
#define __SUDOKU__

#include <vector>
#include <array>
#include <stack>
#include <queue>
#include <cstddef>
#include <algorithm>
#include <utility>
#include <limits>
#include <stdexcept>
#include <optional>
#include <iostream>

using myuint = std::size_t; // change this to increase size

struct Solved
{
	myuint position;
	myuint bit;
	Solved(const myuint& position, const myuint& bit)
		: position(position)
		, bit(bit)
    {};
};

template <myuint N>
using Grid = std::array<myuint, N>;

template <myuint N>
using Peers = std::array<myuint, N>;

template<myuint c_block_size>
class SudokuSolver
{
	public:
		static constexpr myuint c_side_len = c_block_size * c_block_size;
		static constexpr myuint c_total_cells = c_side_len * c_side_len;
		static constexpr myuint c_peer_count = (c_side_len - 1) + (c_side_len - c_block_size) * 2;

	private:
		std::array<myuint, c_side_len> m_occurences;
		
		myuint get_smallest_unsolved(const Grid<c_total_cells>& grid) const
		{
			myuint best = c_side_len + 1;
			myuint pos = grid.size();
			for(myuint i = 0; i < grid.size(); ++i)
			{
				myuint c = __builtin_popcount(grid[i]);
				if(c == 2)
					return i;
				else if(c > 2 && c < best)
				{
					best = c;
					pos = i;
				}
			}
			return pos;
		}
		const std::vector<myuint> get_possible_values(const myuint& value) const
		{
			std::vector<myuint> list;
			list.reserve(c_side_len);
			for(myuint i = 0; i < c_side_len; ++i)
			{
				if(((value) & (1 << i)) != 0)
				{
					list.push_back(i);
				}
			}
			for(myuint i = 0; i < list.size() - 1; ++i)
			{
				for(myuint j = i + 1; j < list.size(); ++j)
				{
					if(m_occurences[i] > m_occurences[j])
					{
						auto tmp = list[i];
						list[i] = list[j];
						list[j] = tmp;
					}
				}
			}
			return list;
		}
		
		static Peers<c_total_cells * c_peer_count> compute_peers()
		{
			Peers<c_total_cells * c_peer_count> peers;
			for(myuint i = 0; i < c_total_cells; ++i)
			{
				const myuint ix = i % c_side_len;
				const myuint iy = i / c_side_len;
				const myuint bx = ix - ix % c_block_size;
				const myuint by = iy - iy % c_block_size;
				myuint n = 0;
				myuint block_corner = bx + by * c_side_len;
				for(myuint x = 0; x < c_block_size; ++x)
				{
					for(myuint y = 0; y < c_block_size; ++y)
					{
						const myuint p = block_corner + x + y * c_side_len;
						if(p != i)
						{
							peers[i * c_peer_count + n++] = p;
						}
					}
				}
				const myuint cy = i - ix;
				for(myuint x = 0; x < c_side_len; ++x)
				{
					if(x < bx || x >= bx + c_block_size)
					{
						peers[i * c_peer_count + n++] = x + cy;
					}
				}
				for(myuint y = 0; y < c_side_len; ++y)
				{
					if(y < by || y >= by + c_block_size)
					{
						peers[i * c_peer_count + n++] = ix + y * c_side_len;
					}
				}
			}
			return peers;
		}
		Peers<c_total_cells * c_peer_count> c_peers;
		
		inline myuint highest_bit(const myuint& v)
		{
			return std::numeric_limits<myuint>::digits - __builtin_clzll(v) - 1;
		}
		
		bool propagate(Grid<c_total_cells>& grid, std::queue<Solved>& queue)
		{
			while(!queue.empty())
			{
				
				const Solved src = queue.front();
				queue.pop();
				for(myuint i = 0; i < c_peer_count; ++i)
				{
					const auto& p = c_peers[src.position * c_peer_count + i];
					auto& peer = grid[p];
					if((peer & (peer - 1)) == 0) // is solved?
					{
						if(src.bit == highest_bit(peer)) // check if same
						{
							std::queue<Solved> empty;
							queue.swap(empty); // clear queue
							return false;
						}
					}
					else
					{
						peer = peer & ~(1 << src.bit); // lower down bit
						if((peer & (peer - 1)) == 0) // is solved?
						{
							auto solved = highest_bit(peer);
							m_occurences[solved]++;
							queue.emplace(p, solved);
						}
					}
				}
			}
			return true;
		}
		
		void format(Grid<c_total_cells>& grid)
		{
			for(myuint i = 0; i < grid.size(); ++i)
			{
				myuint& cell = grid[i];
				if((cell & (cell - 1)) == 0) // is solved?
				{
					cell = highest_bit(cell) + 1;
				}
				else cell = 0;
			}
		}
		
	public:
		SudokuSolver() {
			static_assert(c_block_size > 1, "Block Size must be at least 2.");
			if constexpr(c_side_len >= std::numeric_limits<myuint>::digits)
			{
				 throw std::invalid_argument("c_side_len exceeds the number of bits in myuint");
			}
			c_peers = compute_peers();
		};
		std::optional<Grid<c_total_cells>> solve(const std::vector<myuint>& input)
		{
			if(input.size() != c_total_cells)
				throw std::invalid_argument("Invalid Input Grid Size.");
			std::optional<Grid<c_total_cells>> result;
			std::queue<Solved> queue;
			
			for(myuint i = 0; i < m_occurences.size(); ++i)
				m_occurences[i] = 0;
			
			Grid<c_total_cells> grid;
			for(myuint i = 0; i < input.size(); ++i)
			{
				if(input[i] > c_side_len + 1)
					throw std::invalid_argument("Invalid Grid Cell Value.");
				if(input[i] == 0)
				{
					grid[i] = ((1 << (c_side_len)) - 1);
				}
				else
				{
					myuint z0 = input[i] - 1;
					grid[i] = (1 << z0);
					queue.emplace(i, z0);
					m_occurences[z0]++;
				}
			}
			if(!propagate(grid, queue))
			{
				return result;
			}
			std::stack<Grid<c_total_cells>> stack;
			stack.push(grid);
			while(!stack.empty())
			{
				grid.swap(stack.top());
				stack.pop();
				const myuint pos = get_smallest_unsolved(grid);
				if(pos < grid.size())
				{
					const std::vector<myuint> values = get_possible_values(grid[pos]);
					for(const myuint& v : values)
					{
						Grid<c_total_cells> cpy = grid;
						cpy[pos] = (1 << v);
						queue.emplace(pos, v);
						if(propagate(cpy, queue))
						{
							stack.push(cpy);
						}
					}
				}
				else // grid is solved
				{
					format(grid);
					result = grid;
					return result;
				}
			}
			return result;
		}
		
		void print(const Grid<c_total_cells>& grid) const
		{
			for(myuint i = 0; i < grid.size(); ++i)
			{
				if(grid[i] == 0)
					std::cout << "_";
				else
					std::cout << grid[i];
				if(i % c_side_len == c_side_len - 1)
					std::cout << std::endl;
			}
		}
};

#endif