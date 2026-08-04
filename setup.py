from setuptools import setup, find_packages

setup(
    name="solarscan",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "numpy",
        "pyyaml",
        "matplotlib",
        "reportlab",
    ],
    entry_points={
        "console_scripts": [
            "solarscan=solarscan.cli:main",
        ],
    },
)
