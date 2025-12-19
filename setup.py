#!/usr/bin/env python3
"""Setup script for Antigravity Decryptor."""

from setuptools import setup
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="antigravity-decryptor",
    version="1.1.0",
    author="Arash Zolfaghari",
    description="A portable tool to decrypt and extract conversations from Antigravity IDE's encrypted files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arashz/antigravity_decryptor",
    py_modules=["antigravity_decrypt"],
    install_requires=requirements,
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "antigravity-decrypt=antigravity_decrypt:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="antigravity ide decrypt conversation protobuf encryption",
)
