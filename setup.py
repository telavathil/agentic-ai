from setuptools import setup, find_packages

def read_version():
    with open("VERSION", "r", encoding="utf-8") as f:
        return f.read().strip()

setup(
    name="agentic-ai",
    version=read_version(),
    packages=find_packages(),
    install_requires=[
        "anthropic",
        "pydantic>=2.0.0",
        "python-dotenv",
    ],
)
