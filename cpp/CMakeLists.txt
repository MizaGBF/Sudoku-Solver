cmake_minimum_required(VERSION 3.28)

project(SudokuSolver LANGUAGES CXX)

set(CMAKE_BUILD_TYPE Release)
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

add_executable(main src/main.cpp)
target_link_libraries(main -static)
