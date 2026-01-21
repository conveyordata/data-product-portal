import os
from typing import TYPE_CHECKING

from jinja2 import Template

from app.authorization.service import AuthorizationService
from app.data_products.output_ports.service import OutputPortService
from app.database.database import get_db_session

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def seed_db(path: str, **template_vars):
    db: Session = next(get_db_session())

    # Read the file content
    with open(path, "r") as file:
        file_content = file.read()

    # Render the template with provided variables and environment variables
    template = Template(file_content)
    rendered_content = template.render(**template_vars, **os.environ)

    raw_connection = db.get_bind().raw_connection()
    raw_cursor = raw_connection.cursor()
    raw_cursor.execute(rendered_content)

    raw_connection.commit()
    AuthorizationService(db).reload_enforcer()
    OutputPortService(db).recalculate_all_embeddings()
