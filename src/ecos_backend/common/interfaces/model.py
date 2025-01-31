import abc
import typing

from dataclasses import asdict, dataclass


@dataclass
class AbstractModel(abc.ABC):
    """
    Base model, from which any domain model should be inherited.
    """

    async def to_dict(
        self,
        exclude: typing.Optional[set[str]] = None,
        include: typing.Optional[dict[str, typing.Any]] = None,
    ) -> dict[str, typing.Any]:
        """
        Create a dictionary representation of the model.

        exclude: set of model fields, which should be excluded from dictionary representation.
        include: set of model fields, which should be included into dictionary representation.
        """

        data: dict[str, typing.Any] = asdict(self)

        if exclude is not None:
            for key in exclude:
                try:
                    del data[key]
                except KeyError:
                    pass

        if include is not None:
            data.update(include)

        return data
