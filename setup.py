from setuptools import setup
from setuptools import find_packages

MAJOR = 0
MINOR = 1
MICRO = 0

version = f'{MAJOR}.{MINOR}.{MICRO}'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="alias4sbml",
    version=version,
    author="Adel Heydarabadipour",
    author_email="adelhp@uw.edu",
    description="Create alias nodes for heavily connected nodes in an SBML model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adelhpour/Alias4SBML",
    project_urls={
        "Bug Tracker": "https://github.com/adelhpour/Alias4SBML/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["python-libsbml", "SBMLDiagrams==1.3.2"],
    scripts=["testcases/mid_size_model.py", "testcases/model_with_highly_connected_species.py", "testcases/model_with_no_visualization_info.py", "testcases/model_with_visualization_info.py"],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8"
)
