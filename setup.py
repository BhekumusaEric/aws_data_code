from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="student-insights-pipeline",
    version="1.0.0",
    author="Sibusiso Skhosana, Eric Noah Ntshwenya, Israel Mbuyu",
    author_email="siskhoscjc025@student.wethinkcode.co.za",
    description="A smart data engineering solution for student performance insights",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/student-insights-pipeline",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "flake8>=7.0.0",
            "moto>=4.2.14",
        ],
        "local": [
            "localstack>=3.0.2",
            "awscli>=1.32.34",
        ],
    },
    entry_points={
        "console_scripts": [
            "student-insights=src.cli:main",
        ],
    },
)
