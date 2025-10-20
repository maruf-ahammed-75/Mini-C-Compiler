class VariableRegistry:
    def __init__(self):
        self.scope_stack = [{}]
        self.scope_names = ['global']
        self.current_scope_id = 0

    def add(self, identifier, var_type, initial_val=None, context='declaration'):
        current_scope = self.scope_stack[-1]
        current_scope[identifier] = {
            'id': identifier,
            'dtype': var_type,
            'val': initial_val,
            'ctx': context,
            'scope': self.scope_names[-1],
            'scope_level': len(self.scope_stack) - 1
        }

    def find(self, identifier):
        for scope in reversed(self.scope_stack):
            if identifier in scope:
                return scope[identifier]
        return None

    def find_in_current_scope(self, identifier):
        current_scope = self.scope_stack[-1]
        return current_scope.get(identifier)

    def update(self, identifier, new_value):
        for scope in reversed(self.scope_stack):
            if identifier in scope:
                scope[identifier]['val'] = new_value
                return True
        return False

    def all_entries(self):
        all_vars = []
        for scope in self.scope_stack:
            for var_info in scope.values():
                all_vars.append(var_info)
        return all_vars

    def current_scope_entries(self):
        current_scope = self.scope_stack[-1]
        return list(current_scope.values())

    def push_scope(self, scope_name=None):
        if scope_name is None:
            self.current_scope_id += 1
            scope_name = f"scope_{self.current_scope_id}"
        self.scope_stack.append({})
        self.scope_names.append(scope_name)

    def pop_scope(self):
        if len(self.scope_stack) > 1:
            popped_scope = self.scope_stack.pop()
            self.scope_names.pop()
            return popped_scope
        return None

    def get_scope_level(self):
        return len(self.scope_stack) - 1

    def get_current_scope_name(self):
        return self.scope_names[-1]

    def is_declared_in_current_scope(self, identifier):
        return identifier in self.scope_stack[-1]

    def clear(self):
        self.scope_stack = [{}]
        self.scope_names = ['global']
        self.current_scope_id = 0

    def show(self, include_values=True):
        """
        Return and print a formatted dump of all scopes and their variables.

        Args:
            include_values (bool): If True include current variable values in the output.

        Returns:
            str: The formatted multi-line string representation of the symbol table.
        """
        lines = []
        for level, (scope, name) in enumerate(zip(self.scope_stack, self.scope_names)):
            lines.append(f"Scope level {level} ({name}):")
            if not scope:
                lines.append("  <empty>")
                continue
            # Keep stable ordering for readability
            for ident in sorted(scope.keys()):
                info = scope[ident]
                if include_values:
                    lines.append(
                        f"  {ident}: type={info.get('dtype')}, val={info.get('val')}, ctx={info.get('ctx')}"
                    )
                else:
                    lines.append(
                        f"  {ident}: type={info.get('dtype')}, ctx={info.get('ctx')}"
                    )
        out = '\n'.join(lines)
        print(out)
        return out