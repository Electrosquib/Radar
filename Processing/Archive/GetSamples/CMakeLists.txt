cmake_minimum_required(VERSION 3.10)
project(uhd_test)

set(CMAKE_CXX_STANDARD 17)

set(UHD_DIR /opt/homebrew/lib/cmake/uhd)
find_package(UHD REQUIRED)

add_executable(main main.cpp)

target_link_libraries(main PRIVATE UHD::UHD)
target_include_directories(main PRIVATE /opt/homebrew/include)