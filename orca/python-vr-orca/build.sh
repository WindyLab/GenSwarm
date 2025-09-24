#!/bin/bash

# Build script for VR-ORCA Python interface
# This script automates the build process for the VR-ORCA Python bindings

set -e  # Exit on any error

echo "VR-ORCA Python Interface Build Script"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "Error: setup.py not found. Please run this script from the python-vr-orca directory."
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "Python version: $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)"; then
    echo "Error: Python 3.6 or higher is required"
    exit 1
fi

# Check if required tools are available
echo "Checking build dependencies..."

if ! command -v cmake &> /dev/null; then
    echo "Error: CMake is required but not installed"
    echo "Please install CMake 3.10 or higher"
    exit 1
fi

cmake_version=$(cmake --version | head -n1 | awk '{print $3}')
echo "CMake version: $cmake_version"

# Check C++ compiler
if ! command -v g++ &> /dev/null && ! command -v clang++ &> /dev/null; then
    echo "Error: C++ compiler (g++ or clang++) is required"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
find . -name "*.so" -delete
find . -name "*.cpp" -path "*/src/*" -delete  # Remove generated Cython files

# Check if VR-ORCA source exists
if [ ! -d "../vr-orca/src" ]; then
    echo "Error: VR-ORCA source directory not found at ../vr-orca/src"
    echo "Please ensure the VR-ORCA C++ source is available"
    exit 1
fi

echo "VR-ORCA source found at ../vr-orca/src"

# Build the extension
echo "Building VR-ORCA Python extension..."
python3 setup.py build_ext --inplace

# Install in development mode (optional)
read -p "Install in development mode? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing in development mode..."
    pip3 install -e .
fi

# Run tests
echo "Running basic tests..."
if python3 -c "import vrorca; print('VR-ORCA import successful')"; then
    echo "✓ Basic import test passed"
else
    echo "✗ Basic import test failed"
    exit 1
fi

# Run comprehensive tests if available
if [ -f "test.py" ]; then
    echo "Running comprehensive tests..."
    python3 test.py
else
    echo "Comprehensive test suite not found (test.py missing)"
fi

echo ""
echo "Build completed successfully!"
echo ""
echo "You can now use VR-ORCA in Python:"
echo "  import vrorca"
echo "  sim = vrorca.PyVRORCASimulator(1/60., 1.5, 5, 1.5, 2, 0.4, 2, 1.0)"
echo ""
echo "Run 'python3 example.py' to see usage examples."