"""Setup script for LLMLab CLI."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="llmlab-cli",
    version="0.1.0",
    author="LLMLab",
    author_email="team@llmlab.dev",
    description="Unified API gateway CLI for LLM providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/llmlab/llmlab-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "httpx>=0.24.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llmlab=llmlab.main:cli",
        ],
    },
)
