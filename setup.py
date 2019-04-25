#!/usr/bin/env python3.1
from distutils.core import setup

setup(name="valsimp",
      version="0.1",
      description="Validation framework for scientifical simulation packages",
      author="Bálint Aradi",
      author_email="baradi07@gmail.com",
      url="http://code.google.com/p/valsimp/",
      license="MIT",
      platforms="platform independent",
      package_dir={"": "src"},
      packages=["valsimp",
                "valsimp.io",
                "valsimp.files",
                ],
      scripts=["bin/valsimp", ],
      data_files=[("share/doc/valsimp", ["LICENSE",])],
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        ],
      long_description="""
Validation framework for scientifical simulation packages
---------------------------------------------------------

ValSimP is a lightweight extensible validation framework for
scientific simulation packages. It tests the outcome of simulations
against reference data to ensure that a simulation package works the
expected way.

In the typical scenario developers of scientific simulation packages
set up test suites with ValSimP which are then distributed together with
the simulation software. After compiling/installing the program the end
user uses ValSimP to test whether his local installation works as
expected. ValSimP can be also easily extended by the end users to adapt
the validation procedure to their local environment (e.g. running the
simulations via a queue system).

Requires Python 3.1 or later and NumPy.
"""
     )
