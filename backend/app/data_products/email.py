import functools
from typing import Callable, Sequence

import emailgen

from app.abstract_data_product.model import AbstractDataProduct
from app.core.email.send_mail import send_mail
from app.data_products.output_ports.model import OutputPort
from app.settings import settings
from app.users.schema import User


def send_dataset_link_email(
    data_product: AbstractDataProduct,
    output_port: OutputPort,
    *,
    requester: User,
    approvers: Sequence[User],
) -> Callable[[None], None]:
    url = (
        settings.HOST.strip("/") + "/datasets/" + str(output_port.id) + "#data-product"
    )
    action = emailgen.Table(
        ["Data Product", "Request", "Dataset", "Owned By", "Requested By"]
    )
    action.add_row(
        [
            data_product.name,
            "Access to consume data from ",
            output_port.name,
            ", ".join(
                [
                    f"{approver.first_name} {approver.last_name}"
                    for approver in approvers
                ]
            ),
            f"{requester.first_name} {requester.last_name}",
        ]
    )

    return functools.partial(
        send_mail,
        recipients=approvers,
        action=action,
        url=url,
        subject=f"Action Required: {data_product.name} wants"
        f" to consume data from {output_port.name}",
    )
