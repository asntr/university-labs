cmake_minimum_required(VERSION 3.7)
project(pdc)

include_directories(/usr/local/Cellar/gcc/7.2.0/lib/gcc/7/gcc/x86_64-apple-darwin16.7.0/7.2.0/include/)


set(CMAKE_C_COMPILER "/usr/local/Cellar/gcc/7.2.0/bin/gcc-7")
set(CMAKE_CXX_COMPILER "/usr/local/Cellar/gcc/7.2.0/bin/g++-7")

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopenmp -O2")

set(SOURCE_FILES main.cpp)
add_executable(pdc ${SOURCE_FILES})