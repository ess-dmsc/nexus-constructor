from typing import Tuple, List, Optional

import attr
import h5py

from nexus_constructor.nexus.nexus_wrapper import get_nx_class


class NexusFormatError(Exception):
    pass


@attr.s
class ValidateDataset:
    """
    name: Group must contain a dataset with this name
    shape: Dimensions with None are allowed any length
    attributes: Dictionary item with value of None means allowed to have any value for this attribute. Don't check value for floats
    """

    name = attr.ib(type=str)
    shape = attr.ib(type=Tuple[Optional[int]], default=None)
    attributes = attr.ib(type=dict, default=None)

    def check(self, parent_group: h5py.Group, problems: List):
        dataset = self._find_dataset(parent_group, problems)
        if dataset is not None:
            self._check_shape(dataset, problems)
            self._check_attributes(dataset, problems)
        return problems

    def _find_dataset(
        self, group: h5py.Group, problems: List
    ) -> Optional[h5py.Dataset]:
        for node in group:
            if node == self.name:
                return group[self.name]
        problems.append(
            f"Expected {group.name} to contain a dataset called {self.name}"
        )
        return None

    def _check_shape(self, dataset: h5py.Dataset, problems: List):
        if self.shape is not None:
            dataset_shape = dataset[...].shape
            dims_in_dataset = len(dataset_shape)
            expected_dims = len(self.shape)
            if dims_in_dataset != expected_dims:
                problems.append(
                    f"Expected number of dimensions in {self.name} dataset to be {expected_dims} but it was {dims_in_dataset}"
                )
                return
            for index, dimension_length in enumerate(self.shape):
                if dimension_length is not None:
                    if dataset_shape[index] != dimension_length:
                        problems.append(
                            f"Expected dimension {index} of {self.name} to have a size of {dimension_length} but it was {dataset_shape[index]}"
                        )

    def _check_attributes(self, dataset: h5py.Dataset, problems: List):
        if self.attributes is not None:
            for attribute, value in self.attributes.items():
                if attribute in dataset.attrs:
                    if value is not None:
                        if dataset.attrs[attribute] != value:
                            problems.append(
                                f"Expected {attribute} attribute in {self.name} to have a value of '{value}' but"
                                f" it was '{dataset.attrs[attribute]}'"
                            )
                else:
                    problems.append(
                        f"Expected to find {attribute} attribute in {self.name}"
                    )


def _check_nx_class(group: h5py.Group, nx_class: str, problems: List):

    group_nx_class = get_nx_class(group)

    if not group_nx_class:
        problems.append(f"Expected {group.name} to have an NX_class attribute")
    elif group_nx_class != nx_class:
        problems.append(
            f"Expected {group.name} to have NX_class attribute of {nx_class} but it was {group.attrs['NX_class']}"
        )


def validate_group(
    group: h5py.Group, nx_class: str, dataset_details: Tuple[ValidateDataset, ...]
) -> List:
    problems = []
    _check_nx_class(group, nx_class, problems)
    for dataset in dataset_details:
        dataset.check(group, problems)
    return problems
