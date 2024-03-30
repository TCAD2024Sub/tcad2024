cmake_minimum_required(VERSION 3.13)  # CMake version check
project(simple_example)               # Create project "simple_example"
set(CMAKE_CXX_STANDARD 14)            # Enable c++14 standard



# Add executable target with source files listed in SOURCE_FILES variable
add_executable(sa
        sa_pipeline/main.cpp
        sa_pipeline/pipeline_sa_sw.cpp
        sa_pipeline/fifo_sa_sw.cpp
        sa_pipeline/stage0_sa_sw.cpp
        sa_pipeline/stage1_sa_sw.cpp
        sa_pipeline/stage2_sa_sw.cpp
        sa_pipeline/stage3_sa_sw.cpp
        sa_pipeline/stage4_sa_sw.cpp
        sa_pipeline/stage5_sa_sw.cpp
        sa_pipeline/stage6_sa_sw.cpp
        sa_pipeline/stage8_sa_sw.cpp
        sa_pipeline/stage7_sa_sw.cpp
        sa_pipeline/stage8_sa_sw.cpp
        sa_pipeline/stage9_sa_sw.cpp
        sa_pipeline/util_sa_sw.cpp
)