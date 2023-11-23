from setuptools import find_packages, setup

setup(
    name="scor",
    version="0.1",
    packages=find_packages(include=["scor", "scor.*"]),
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "black==23.11.0",
            "isort==5.12.0",
        ]
    },
)
