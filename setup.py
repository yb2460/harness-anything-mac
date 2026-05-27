"""cli-anything-WPS-mac - Cross-platform office automation CLI."""
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-WPS-mac",
    version="1.0.0",
    description="Cross-platform office automation -- WPS COM on Windows, LibreOffice on macOS/Linux",
    author="yb2460",
    python_requires=">=3.10",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
        'pywin32>=305; platform_system=="Windows"',
    ],
    extras_require={"dev": ["pytest", "pytest-cov"]},
    entry_points={
        "console_scripts": [
            "cli-anything-office=cli_anything.office.office_cli:main",
        ],
    },
    package_data={"cli_anything.office": ["skills/*.md"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
)
