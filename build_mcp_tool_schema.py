import inspect
from typing import get_type_hints
import mcp.types as types


def build_tool_schema(func):
    doc = func.__doc__ or ""
    lines = [line.strip() for line in doc.strip().splitlines() if line.strip()]
    description = lines[0] if lines else "No description available."

    hints = get_type_hints(func)
    input_schema = {
        "type": "object",
        "required": [],
        "properties": {}
    }

    for arg, hint in hints.items():
        if arg == 'return':
            continue
        input_schema["required"].append(arg)
        input_schema["properties"][arg] = {
            "type": "string",  # default, could expand to match hint
            "description": "No description"
        }

    # Optionally try to extract argument descriptions from the docstring
    for line in lines[1:]:
        if ':' in line:
            arg, desc = line.split(':', 1)
            arg = arg.strip()
            if arg in input_schema["properties"]:
                input_schema["properties"][arg]["description"] = desc.strip()

    # Determine output type
    return_type = hints.get("return", str)
    return_type_name = return_type.__name__ if hasattr(return_type, '__name__') else str(return_type)

    return types.Tool(
    name=func.__name__,
    description=description,
    inputSchema=input_schema# fallback
    )
