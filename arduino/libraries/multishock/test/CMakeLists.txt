
cmake_minimum_required(VERSION 2.8)

# TODO version #?
project(multishock_tests)

# TODO why no prefix required here?
include(gtest.cmake)

# TODO so disabled by default?
SET(COVERAGE OFF CACHE BOOL "Coverage")

# TODO variable for name here and project above?
add_executable(multishock_tests unit_tests.cpp)

# because gtest requires the pthreads library, and I suppose this installs that
find_package (Threads)
target_link_libraries(tests gtest ${CMAKE_THREAD_LIBS_INIT})

# TODO actually test the windows part?
if (MSVC)
    target_compile_options(tests PRIVATE /std:c++17 /W4 /WX)

    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Ox")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Od")

    # VS 2017 removed tr1
    add_definitions(-DGTEST_HAS_TR1_TUPLE=0)

    # TODO no coverage checking in windows? why? coverall just not work here?
else()
    target_compile_options(tests PRIVATE -std=c++14 -g -Wall -Werror -Wextra \
        -Wpedantic -Wconversion -Wswitch-default -Wswitch-enum \
	-Wunreachable-code -Wwrite-strings -Wcast-align -Wshadow -Wundef)

    if (COVERAGE)
        target_compile_options(tests PRIVATE --coverage)
        target_link_libraries(tests PRIVATE --coverage)
    endif()
endif()
