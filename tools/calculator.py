"""A calculator tool that safely evaluates mathematical expressions using Python's AST."""

import ast
import math
import operator
import json
from typing import Dict, Any

from .base import Tool


class Calculator(Tool):
    """A tool for performing mathematical calculations with support for basic arithmetic,
    trigonometric functions, and logarithms."""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="""Performs mathematical calculations. Supports basic arithmetic,
            trigonometric functions, logarithms, etc.""",
        )

        # Define safe operations
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.Mod: operator.mod,
        }

        self.functions = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "abs": abs,
            "round": round,
        }

    def get_example(self) -> str:
        """Return an example of how to use the calculator tool."""
        example = {
            "expression": "1000 * (1 + 0.05)**3"  # Compound interest example
        }
        return json.dumps(example)

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate",
                }
            },
            "required": ["expression"],
        }

    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Safely evaluate a mathematical expression"""
        expression = parameters.get("expression", "")

        if not expression:
            return {"error": "No expression provided"}

        try:
            return {"result": self._evaluate(expression)}
        except (ValueError, SyntaxError, TypeError) as e:
            return {"error": f"Error evaluating expression: {str(e)}"}

    def _evaluate(self, expression: str) -> float:
        """Safely evaluate a mathematical expression using ast"""
        try:
            # Parse expression
            node = ast.parse(expression, mode="eval").body
            return self._eval_node(node)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}") from e

    def _eval_node(self, node):
        """Recursively evaluate an AST node"""
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, (ast.BinOp, ast.UnaryOp)):
            if type(node.op) not in self.operators:
                raise ValueError(f"Unsupported operation: {type(node.op).__name__}")
            if isinstance(node, ast.BinOp):
                return self.operators[type(node.op)](
                    self._eval_node(node.left), self._eval_node(node.right)
                )
            return self.operators[type(node.op)](self._eval_node(node.operand))
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls are supported")
            func_name = node.func.id
            if func_name not in self.functions:
                raise ValueError(f"Unsupported function: {func_name}")
            args = [self._eval_node(arg) for arg in node.args]
            return self.functions[func_name](*args)
        if isinstance(node, ast.Name):
            constants = {"pi": math.pi, "e": math.e}
            if node.id not in constants:
                raise ValueError(f"Unknown variable: {node.id}")
            return constants[node.id]
        raise ValueError(f"Unsupported node type: {type(node).__name__}")
