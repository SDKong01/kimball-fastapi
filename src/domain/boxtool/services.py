from typing import List, Dict, Any, Union, Optional
from itertools import accumulate, groupby


class Services:
    def __init__(self, data_list: List[Dict[str, Any]]):
        self.data_list = data_list

    def _compute_new_axis_values(
        self,
        axis: List[int],
        ortogonal_axis: List[int],
        axis_key: str,
        ortogonal_axis_key: str,
    ) -> List[Union[int, None]]:
        init_ortogonal, end_ortogonal = ortogonal_axis[0], ortogonal_axis[-1]
        false_values = {"None", None, "null", "nan", "", " "}

        valid_values = {
            item[axis_key]
            for item in self.data_list
            if init_ortogonal <= item[ortogonal_axis_key] <= end_ortogonal
            and item["value"] not in false_values
        }

        return [i if i in valid_values else None for i in axis]

    def _group_sublistas(
        self, new_axis_values: List[Optional[int]]
    ) -> List[List[Optional[int]]]:
        return [
            list(group)
            for key, group in groupby(new_axis_values, key=lambda x: x is not None)
            if key
        ]

    def compute_tables(
        self,
        x_axis: List[int],
        y_axis: List[int],
        is_previous_none: bool = False,
        is_orthogonal: bool = False,
    ):
        new_axis_args = (
            (x_axis, y_axis, "x", "y") if is_orthogonal else (y_axis, x_axis, "y", "x")
        )
        new_axis_values = self._compute_new_axis_values(*new_axis_args)

        if None not in new_axis_values and not is_previous_none:
            return (x_axis[0], y_axis[0]), (x_axis[-1], y_axis[-1])

        sublistas = self._group_sublistas(new_axis_values)
        return list(
            self.compute_tables(
                x_axis=s if is_orthogonal else x_axis,
                y_axis=s if not is_orthogonal else y_axis,
                is_previous_none=None in new_axis_values,
                is_orthogonal=not is_orthogonal,
            )
            for s in sublistas
        )

    def compute_tables_sac_version(
        self,
        sac: List[int],
        x_axis: List[int],
        y_axis: List[int],
        is_previous_none: bool = False,
        is_orthogonal: bool = False,
    ):
        new_axis_args = (
            (x_axis, y_axis, "x", "y") if is_orthogonal else (y_axis, x_axis, "y", "x")
        )
        new_axis_values = self._compute_new_axis_values(*new_axis_args)

        if None not in new_axis_values and not is_previous_none:
            sac.append(((x_axis[0], y_axis[0]), (x_axis[-1], y_axis[-1])))
            return (x_axis[0], y_axis[0]), (x_axis[-1], y_axis[-1])

        sublistas = self._group_sublistas(new_axis_values)
        return list(
            self.compute_tables_sac_version(
                x_axis=s if is_orthogonal else x_axis,
                y_axis=s if not is_orthogonal else y_axis,
                is_previous_none=None in new_axis_values,
                is_orthogonal=not is_orthogonal,
                sac=sac,
            )
            for s in sublistas
        )

    def execute(self):
        x_axis = sorted({d["x"] for d in self.data_list})
        y_axis = sorted({d["y"] for d in self.data_list})
        response = []
        self.compute_tables_sac_version(
            x_axis=x_axis, y_axis=y_axis, is_previous_none=True, sac=response
        )
        return response
