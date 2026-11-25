from typing import TYPE_CHECKING, Any

from factory.alchemy import SQLAlchemyModelFactory


class ModelFactory[T](SQLAlchemyModelFactory):
    class Meta:
        abstract = True

    if TYPE_CHECKING:

        def __new__(cls, **kwargs: Any) -> T: ...  # type: ignore[misc]
