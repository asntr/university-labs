cmake_minimum_required(VERSION 3.7)
project(lab2)

set(CMAKE_CXX_STANDARD 11)

set(CMAKE_C_COMPILER "/usr/local/bin/mpicc")

set(CMAKE_CXX_COMPILER "/usr/local/bin/mpic++")

set(SOURCE_FILES main.cpp)
add_executable(lab2 ${SOURCE_FILES})