cmake_minimum_required(VERSION 3.10)
project(python-vr-orca)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and required packages
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Add the VR-ORCA subdirectory to build the C++ library
add_subdirectory(../vr-orca vr-orca-build)

# Set compile flags for position-independent code
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")

# Export the library for use by setup.py
install(TARGETS RVO 
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

# Export headers
install(DIRECTORY ../vr-orca/src/ 
        DESTINATION include
        FILES_MATCHING PATTERN "*.h")