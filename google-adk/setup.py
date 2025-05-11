from setuptools import setup, find_packages

setup(
    name="noaa-tides-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-adk",
        "python-dotenv",
        "pytest",
        "pytest-asyncio",
    ],
    python_requires=">=3.8",
) 