cmake_minimum_required(VERSION 3.15)
project(SudokuSolver LANGUAGES CXX)

# Allow user to override; default to Release for single-config generators
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING
      "Choose the build type: Debug Release RelWithDebInfo MinSizeRel"
      FORCE)
endif()

# Set C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Set output directory
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")

# Gather all source files
file(GLOB_RECURSE SRC_FILES
  "src/*.cpp"
  "src/*.c"
)
set(SRC ${SRC_FILES})

# Add executable
add_executable(main ${SRC})

# Set build exe names
set_target_properties(main PROPERTIES
  OUTPUT_NAME_DEBUG  "debug"
  OUTPUT_NAME_RELEASE "main"
  OUTPUT_NAME_RELWITHDEBINFO "debug_o"
  OUTPUT_NAME_MINSIZEREL "main_s"
)

# Add static option
option(BUILD_STATIC_RUNTIME "Link the C/C++ runtime statically" OFF)
if(BUILD_STATIC_RUNTIME)
  target_link_options(main PRIVATE "-static")
endif()

# Specific compiler options
target_compile_features(main PRIVATE cxx_std_17)
target_compile_options(main PRIVATE
  $<$<CXX_COMPILER_ID:GNU>:-Wall -Wextra -Wpedantic>
  $<$<CXX_COMPILER_ID:Clang>:-Wall -Wextra -Wpedantic>
  $<$<CXX_COMPILER_ID:MSVC>:/W4>
)