import os
from jinja2 import Template


def get_html_template(filename: str) -> str:
    with open(os.path.join("templates", filename)) as f:
        return f.read()


def render_html_template(filename: str, data: dict[str, str] = {}) -> str:
    template = Template(get_html_template(filename))
    return template.render(data)
