"""Agentic AI - An AI agent framework."""

def read_version():
    with open("VERSION", encoding="utf-8") as f:
        return f.read().strip()

__version__ = read_version()
