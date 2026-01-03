from setuptools import setup, Extension
import pybind11
import sys

# Define the extension module
ext_modules = [
    Extension(
        "invariant_enforcement",
        sources=[
            "ai_execution_boundary/enforcement/bindings/pybind.cpp",
            "ai_execution_boundary/enforcement/runtime/boundary.cpp"
        ],
        include_dirs=[
            pybind11.get_include(),
            "ai_execution_boundary/enforcement/runtime"
        ],
        language='c++',
        extra_compile_args=['-std=c++17'],
    ),
]

setup(
    name="invariant_enforcement",
    version="0.1.0",
    ext_modules=ext_modules,
)
