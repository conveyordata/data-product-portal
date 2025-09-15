import functools
from typing import Callable, Sequence

import emailgen

from app.core.email.send_mail import send_mail
from app.data_outputs.schema import DataOutput
from app.datasets.schema import Dataset
from app.settings import settings
from app.users.schema import User


def send_link_dataset_email(
    dataset: Dataset,
    data_output: DataOutput,
    *,
    requester: User,
    approvers: Sequence[User],
) -> Callable[[None], None]:
    url = settings.HOST.strip("/") + "/datasets/" + str(dataset.id) + "#data-output"
    action = emailgen.Table(
        ["Data Product", "Request", "Dataset", "Owned By", "Requested By"]
    )
    action.add_row(
        [
            data_output.owner.name,
            "Wants to provide data to ",
            dataset.name,
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
        subject=f"Action Required: {data_output.owner.name}"
        f" wants to provide data to {dataset.name}",
    )
