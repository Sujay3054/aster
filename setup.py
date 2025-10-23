from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aster-python-sdk",
    version="1.0.0",
    author="Aster SDK Team",
    author_email="contact@asterdex.com",
    description="Professional Python SDK for Aster DEX trading platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aster-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "analysis": [
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
            "ta-lib>=0.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aster-sdk=aster_sdk.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)