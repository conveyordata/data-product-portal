import os


def get_boolean_variable(name: str, default_value: bool | None = None) -> bool:
    true_ = (
        "true",
        "1",
        "t",
        "y",
        "yes",
        "on",
    )  # Add more entries if you want, like: `y`, `yes`, `on`, ...
    false_ = (
        "false",
        "0",
        "f",
        "n",
        "no",
        "off",
    )  # Add more entries if you want, like: `n`, `no`, `off`, ...
    value: str | None = os.getenv(name, None)
    if value is None:
        if default_value is None:
            raise ValueError(f"Variable `{name}` not set!")
        else:
            value = str(default_value)
    if value.lower() not in true_ + false_:
        raise ValueError(f"Invalid value `{value}` for variable `{name}`")
    return value.lower() in true_
