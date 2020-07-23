import attr
from typing import List, Dict, Any
import numpy as np

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.model.node import Node
from nexus_constructor.model.value_type import ValueType, VALUE_TYPE


def _get_human_readable_type(new_value: Any):
    if isinstance(new_value, list):
        new_value = new_value[0]
    if isinstance(new_value, str):
        return "String"
    elif isinstance(new_value, int):
        return "Int"
    elif isinstance(new_value, float):
        return "Double"
    else:
        return next(
            key for key, value in VALUE_TYPE.items() if value == new_value.dtype
        )


@attr.s
class DatasetMetadata:
    type = attr.ib(type=str)
    size = attr.ib(factory=tuple)

    def as_dict(self) -> Dict:
        return {"size": self.size, "type": self.type}


def create_metadata(ds: "Dataset") -> DatasetMetadata:
    """
    Attempts to infer size and type from the value passed at initialisation.
    :param ds: the dataset to infer from
    :return: a dataset metadata class containing the size and type of the dataset
    """
    return DatasetMetadata(
        size=len(ds.values) if isinstance(ds.values, list) else "1",
        type=_get_human_readable_type(ds.values),
    )


@attr.s
class Dataset(Node):
    values = attr.ib(factory=list, type=List[ValueType])
    type = attr.ib(type=str, default="dataset", init=False)
    dataset = attr.ib(
        type=DatasetMetadata, default=attr.Factory(create_metadata, takes_self=True)
    )

    @property
    def nx_class(self):
        return self.get_attribute_value(CommonAttrs.NX_CLASS)

    @nx_class.setter
    def nx_class(self, new_nx_class: str):
        self.set_attribute_value(CommonAttrs.NX_CLASS, new_nx_class)

    def as_dict(self) -> Dict[str, Any]:
        return_dict = super().as_dict()
        values = self.values
        if isinstance(values, np.ndarray):
            values = values.tolist()
        return_dict["type"] = self.type
        return_dict["values"] = values
        return_dict["dataset"] = self.dataset.as_dict()
        return return_dict
