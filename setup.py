#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="plurl",
    version="1.0.0",
    author="Play Curl Team",
    author_email="plurl@example.com",
    description="A powerful Playwright + curl-style HTTP testing tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/renaissancebro/curl_observer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Networking :: Monitoring",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "plurl=plurl:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="playwright browser automation api testing curl http",
    project_urls={
        "Bug Reports": "https://github.com/renaissancebro/curl_observer/issues",
        "Source": "https://github.com/renaissancebro/curl_observer",
        "Documentation": "https://github.com/renaissancebro/curl_observer#readme",
    },
)