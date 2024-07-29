from modules.framework.code.function_layer import FunctionLayer
from modules.framework.code.function_node import FunctionNode, State
from modules.framework.context.contraint_info import ConstraintPool
from modules.file.log_file import logger
from modules.file.file import File


class FunctionTree:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.reset()
        return cls._instance

    def __getitem__(self, key: str):
        return self._function_nodes[key]

    def __setitem__(self, key, value):
        if isinstance(key, str):
            self._function_nodes[key] = value

    def reset(self):
        self._function_nodes: dict[str, FunctionNode] = {}
        self.import_list: set[str] = {"from apis import *"}
        self._layers: list[FunctionLayer] = []
        self._index = 0
        self._keys_set = set()
        self._file = File(name="functions.py")
        # self._last_layer = FunctionLayer()
        # self._run_loop = FunctionNode(name="run_loop",
        #                               description="an interface function for users to call, based on existing functions written by other assistants. Users only need to call this function to complete the predetermined task.")
        # self._last_layer.add_function(self._run_loop)
        # self._function_nodes["run_loop"] = self._run_loop

    @property
    def nodes(self):
        return self._function_nodes.values()

    @property
    def names(self):
        return self._function_nodes.keys()

    @property
    def keys_set(self):
        return self._keys_set or set(self.names)

    @property
    def functions_body(self):
        result = [f.function_body for f in self._function_nodes.values()]
        return result

    @property
    def functions_brief(self):
        result = [f.brief for f in self._function_nodes.values()]
        return result

    @property
    def function_valid_content(self):
        result = [f.content for f in self._function_nodes.values() if f.content]
        return result

    def filtered_functions(self, exclude_function: FunctionNode):
        result = [
            value
            for key, value in self._function_nodes.items()
            if key != exclude_function.name
        ]
        return result

    def related_function_content(self, error_msg: str):
        result = [
            value.content
            for key, value in self._function_nodes.items()
            if key in error_msg
        ]
        return result

    def update(self):
        old_layers = self._layers.copy()

        self._reset_layers()
        layer_head = self._get_bottom_layer()
        set_visited_nodes = set()
        self._build_up(layer_head, set_visited_nodes)

        # self._layers.append(self._last_layer)
        self._update_function_to_layer()

        self._clear_changed_function_states(old_layers)
        logger.log(
            f"layers: {[[f.name for f in layer] for layer in self._layers]}",
            level="warning",
        )

    def _update_function_to_layer(self):
        self._function_to_layer = {}
        for layer_index, layer in enumerate(self._layers):
            for function_node in layer:
                self._function_to_layer[function_node] = layer_index

    def _clear_changed_function_states(self, old_layers):
        old_function_to_layer = {
            function_node: layer_index
            for layer_index, layer in enumerate(old_layers)
            for function_node in layer
        }
        for function_node, new_layer in self._function_to_layer.items():
            old_layer = old_function_to_layer.get(function_node)
            if old_layer is not None and old_layer < new_layer:
                function_node.reset()
                logger.log(f"function {function_node.name} reset", level="warning")

    def init_functions(self, content: str):
        constraint_pool = ConstraintPool()
        try:
            for function in eval(content)["functions"]:
                name = function["name"]
                new_node = self._obtain_node(name, description=function["description"])
                from modules.prompt.robot_api_prompt import robot_api
                [
                    new_node.add_callee(self._obtain_node(name=call))
                    for call in function["calls"]
                    if call not in robot_api.apis.keys()
                ]
            self.update()
        except Exception as e:
            logger.log(f"Error in init_functions: {e}", level="error")
            raise Exception

    async def process_function_layer(
        self,
        operation,
        operation_type: State,
        start_layer_index=0,
    ):
        import asyncio

        for index, layer in enumerate(
            self._layers[start_layer_index : start_layer_index + 1]
        ):
            tasks = []
            logger.log(f"Layer: {start_layer_index + index}", "warning")
            for function_node in layer:
                if function_node.state != operation_type:
                    function_node.state = operation_type
                else:
                    continue
                task = asyncio.create_task(operation(function_node))
                tasks.append(task)
            await asyncio.gather(*tasks)

    def _reset_layers(self):
        self._layers.clear()

    def _build_up(self, current_layer: FunctionLayer, set_visited_nodes: set):
        if len(current_layer) > 0:
            self._layers.append(current_layer)
        else:
            return
        next_layer = FunctionLayer()
        for caller in current_layer.set_callers:
            if caller not in set_visited_nodes:
                caller_node = self[caller.name]
                if self._all_callees_in_previous_layers(caller_node):
                    next_layer.add_function(caller_node)
                    set_visited_nodes.add(caller)

        self._build_up(next_layer, set_visited_nodes)

    def _all_callees_in_previous_layers(self, caller_node: FunctionNode) -> bool:
        for callee in caller_node.callees:
            if not any(callee in layer.functions for layer in self._layers):
                return False
        return True

    def _get_bottom_layer(self):
        bottom_layer = [
            func
            for func in self._function_nodes.values()
            if func.callees.isdisjoint(set(self._function_nodes.values()))
        ]
        return FunctionLayer(bottom_layer)

    def set_definition(self, function_name, definition):
        self._function_nodes[function_name]._definition = definition

    def update_from_parser(self, imports: set, function_dict: dict):
        self._update_imports(imports)
        self._update_function_dict(function_dict)
        self.update()

    def get_min_layer_index_by_state(self, state: State) -> int:
        for layer_index, layer in enumerate(self._layers):
            for function_node in layer.functions:
                if function_node.state == state:
                    return layer_index

        return -1

    def save_code(self, function_names):
        for function_name in function_names:
            self.save_by_function(self._function_nodes[function_name])

    def _find_all_relative_functions(self, function: FunctionNode, seen: set = None):
        if seen is None:
            seen = set()
        f_name = function.name

        if function not in seen and f_name in self._function_nodes:
            seen.add(function)
            callees = self._function_nodes[f_name].callees
            [self._find_all_relative_functions(callee, seen) for callee in callees]

        return list(seen)

    def save_functions_to_file(self, functions: list[FunctionNode] = None):
        import_str = "\n".join(sorted(self.import_list))
        if not functions:
            content = "\n\n\n".join([f.content for f in self._function_nodes.values()])
        else:
            content = "\n\n\n".join([f.content for f in functions])
        self._file.message = f"{import_str}\n\n{content}\n"

    def save_by_function(self, function: FunctionNode | str):
        if isinstance(function, str):
            function = self._function_nodes[function]
        relative_function = self._find_all_relative_functions(function)
        logger.log(f"relative_ function: {relative_function}", level="warning")
        self.save_functions_to_file(relative_function)

    def _update_imports(self, imports: set):
        self.import_list |= imports

    def _update_function_dict(self, function_dict: dict[str, str]):
        for name, content in function_dict.items():
            node = self._obtain_node(name, content=content)
            # self._function_tree[name].add_import(self._imports)
            for other_function in self._function_nodes.values():
                if other_function._name != name and other_function._name in content:
                    node.add_callee(other_function)
            logger.log(
                f" function_name: {name}, calls: {self[name].callee_names}",
                level="info",
            )

    def _obtain_node(self, name, description="", content=""):
        if name in self._function_nodes:
            node = self._function_nodes[name]
        else:
            node = FunctionNode(name=name, description=description)
            self._function_nodes[name] = node
        node.content = content or node.content
        node.description = description or node.description

        return node
