from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext
from Cython.Build import cythonize


class BuildVrOrcaExt(_build_ext):
    """Builds VR-ORCA before our module."""

    def run(self):
        # VR-ORCA already built - just proceed with extension build
        _build_ext.run(self)


extensions = [
    Extension('vrorca', ['src/*.pyx'],
              include_dirs=['../vr-orca/src'],
              libraries=['RVO'],
              library_dirs=['../vr-orca/build/src'],
              extra_compile_args=['-fPIC']),
]

setup(
    name="pyvrorca",
    version="1.0.0",
    description="Python bindings for VR-ORCA (Variable Responsibility Optimal Reciprocal Collision Avoidance)",
    long_description="""
    Python bindings for VR-ORCA, an extension of the RVO2 library that implements
    Variable Responsibility Optimal Reciprocal Collision Avoidance. VR-ORCA improves
    upon the standard ORCA algorithm by dynamically adjusting the responsibility
    distribution between agents for collision avoidance.
    
    This library provides a Python interface similar to python-rvo2 but with the
    enhanced VR-ORCA capabilities for better multi-agent navigation.
    """,
    author="GenSwarm Team",
    author_email="contact@genswarm.org",
    url="https://github.com/WestlakeIUSL/GenSwarm",
    ext_modules=cythonize(extensions),
    cmdclass={'build_ext': BuildVrOrcaExt},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Cython',
        'Topic :: Games/Entertainment :: Simulation',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    keywords='robotics, navigation, collision avoidance, multi-agent, simulation, orca, vr-orca',
    python_requires='>=3.6',
    install_requires=[
        'cython>=0.29.0',
        'numpy>=1.18.0',
    ],
)