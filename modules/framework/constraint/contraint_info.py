"""
Copyright (c) 2024 WindyLab of Westlake University, China
All rights reserved.

This software is provided "as is" without warranty of any kind, either
express or implied, including but not limited to the warranties of
merchantability, fitness for a particular purpose, or non-infringement.
In no event shall the authors or copyright holders be liable for any
claim, damages, or other liability, whether in an action of contract,
tort, or otherwise, arising from, out of, or in connection with the
software or the use or other dealings in the software.
"""

from modules.file import File, logger
from .constraint_node import ConstraintNode
from ..parser import parse_text


class ConstraintPool:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.reset()
        return cls._instance

    def reset(self):
        self._constraint_nodes = {}
        self._file = File("constraints.md")

    def __str__(self) -> str:
        result = "\n".join([c.brief for c in self._constraint_nodes.values()])
        return result

    def __getitem__(self, constraint_name):
        if constraint_name in self._constraint_nodes:
            return self._constraint_nodes[constraint_name]
        else:
            logger.log(
                f"Constraint {constraint_name} not found,Current Existing:"
                f"{self._constraint_nodes.values()}",
                level="error",
            )
            raise Exception

    @property
    def constraint_list(self):
        result = [
            constraint.to_json() for constraint in self._constraint_nodes.values()
        ]
        return result

    def filtered_constraints(self, related_constraints: list[ConstraintNode]):
        def check(constraint: ConstraintNode):
            if constraint.name not in self._constraint_nodes:
                logger.log(
                    f"Constraint {constraint.name} is not in the constraint pool",
                    "error",
                )
                raise SystemExit

        [check(key) for key in related_constraints]
        result = "\n".join(
            [
                value.brief
                for key, value in self._constraint_nodes.items()
                if value in related_constraints
            ]
        )
        return result

    def init_constraints(self, content: str):
        def sync_to_file():
            self._file.message = str(self)

        try:
            for constraint in eval(content)["constraints"]:
                name = constraint["name"]
                self._constraint_nodes[name] = ConstraintNode(
                    name=name, description=constraint["description"]
                )
        except Exception as e:
            logger.log(f"Error in init_constraints: {e}", level="error")
            raise Exception
        sync_to_file()

    def check_constraints_satisfaction(self):
        def report_error(constraint: ConstraintNode):
            logger.log(
                f"Constraint {constraint._name} has no satisfying function",
                "error",
            )
            raise Exception(f"Constraint {constraint._name} has no satisfying function")

        [
            report_error(c)
            for c in self._constraint_nodes.values()
            if c.has_no_connections()
        ]
        logger.log("All constraints have satisfying functions", "success")

    def get_constraint_names(self):
        """Returns a set of all constraint names."""
        return set(self._constraint_nodes.keys())
