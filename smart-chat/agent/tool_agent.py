import re
from langchain.agents import Tool

# Handle storing and calculating simple variables and expressions.
class VariableManager:
    def __init__(self):
        self.vars = {}

    # Set a single variable using an expression like 'A = 1'.
    def set_variable(self, expr: str) -> str:
        match = re.match(r"^\s*([A-Za-z]+)\s*=\s*([-\d\.]+)\s*$", expr)
        if match:
            var_name = match.group(1).upper()
            value = float(match.group(2))
            self.vars[var_name] = value
            return f"Stored variable {var_name} = {value}"
        else:
            return "Invalid format. Please use 'VAR=VALUE', e.g., A=1"

    # Evaluate an arithmetic expression, replacing known variables with values.
    def calculate_expression(self, expr: str) -> str:
        safe_expr = expr.upper()

        for var, val in self.vars.items():
            safe_expr = re.sub(rf"\b{var}\b", str(val), safe_expr)

        if not re.match(r"^[\d\.\+\-\*\/\(\) ]+$", safe_expr):
            return "Expression contains invalid characters or unknown variables."

        try:
            result = eval(safe_expr)
            return f"Result: {result}"
        except Exception as e:
            return f"Calculation error: {str(e)}"

    # Main entry for handling input.
    def run(self, input_text: str) -> str:
        input_text = input_text.strip()

        assignments = re.findall(r"\b([A-Za-z]+)\s*=\s*([-\d\.]+)\b", input_text)

        if assignments:
            messages = []
            for var, val in assignments:
                var_name = var.upper()
                try:
                    value = float(val)
                    self.vars[var_name] = value
                    messages.append(f"{var_name} = {value}")
                except ValueError:
                    messages.append(f"Failed to convert {var_name} to a number: {val}")
            return "Stored variables: " + ", ".join(messages)
        else:
            return self.calculate_expression(input_text)

variable_manager = VariableManager()

# Define this as a LangChain tool so it can be used in an agent.
variable_tool = Tool(
    name="variable_manager",
    func=variable_manager.run,
    description=(
        "Allows users to define one or multiple variables and perform calculations using them. "
        "To define variables, use the format 'A=1 B=2 C=3' (case-insensitive). "
        "To perform calculations, use expressions like 'A + B * 2 / (C - 1)'. "
        "Supports basic arithmetic operations: +, -, *, /, and parentheses. "
        "Always return only the final numeric result, without repeating the question or showing step-by-step reasoning."
    )
)
