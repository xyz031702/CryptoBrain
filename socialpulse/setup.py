from setuptools import setup, find_packages

setup(
    name="socialpulse",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "python-dotenv>=0.19.0",
    ],
    author="CryptoBrain Team",
    description="Social media analysis for crypto trends",
)
