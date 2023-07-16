#!/usr/bin/env python3

import inspect
import operator
import os
import sys
import traceback

FILE_EXTENSION = "tea"
VERSION_INFO = "tea version 0.0.2 2023-07-11"
EOF = "EOF"


class Parser:
    @classmethod
    def tokenize(cls, code):
        """Transform code into a list object of tokens."""
        return code.replace('[', ' [ ').replace(']', ' ] ').split()

    @classmethod
    def atomizer(cls, token):
        """Numbers become numbers; every other token is a symbol."""
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return str(token)

    @classmethod
    def to_list(cls, tokens):
        """Convert a list of tokens into a "list" data structure"""

        if len(tokens) == 0:
            raise SyntaxError("Unexpected EOF")

        token = tokens.pop(0)
        if '[' == token:
            _list = []
            while tokens[0] != ']':
                # Recursive deep down
                _list.append(cls.to_list(tokens))
            tokens.pop(0)  # pop off ']'
            return _list
        elif ']' == token:
            raise SyntaxError('Unexpected token "]"')

        return cls.atomizer(token)

    @classmethod
    def parse(cls, code):
        """Parse a code expression."""
        return cls.to_list(cls.tokenize(code))


class Transformer:
    @staticmethod
    def transform_def_to_var_lambda(def_expr):
        name = def_expr[1]
        params = def_expr[2]
        body = def_expr[3]
        return ["var", name, ["lambda", params, body]]

    @staticmethod
    def transform_switch_to_if(switch_expr):
        cases = switch_expr[1:]

        if_expr = ["if", None, None, None]
        current = if_expr

        for index, case in enumerate(cases, start=1):
            [_cond, _block] = cases[index - 1]  # else case
            current[1] = _cond
            current[2] = _block
            [next_cond, next_block] = case

            if next_cond == "else":
                current[3] = next_block
            else:
                current[3] = ["if", None, None, None]

            current = current[3]

        return if_expr

    @staticmethod
    def transform_for_to_while(for_expr):
        [_, init, cond, modifier, body] = for_expr
        return ["begin", init, ["while", cond, ["begin", body, modifier]]]

    @staticmethod  # [set foo [+ foo 1]]
    def transform_incr_to_set(inc_expr):
        [_, expr] = inc_expr
        return ["set", expr, ["+", expr, 1]]

    @staticmethod  # [set foo [- foo 1]]
    def transform_decr_to_set(dec_expr):
        [_, expr] = dec_expr
        return ["set", expr, ["-", expr, 1]]

    @staticmethod  # [set foo [+ foo value]]
    def transform_incr_val_to_set(inc_expr):
        [_, expr, value] = inc_expr
        return ["set", expr, ["+", expr, value]]

    @staticmethod  # [set foo [- foo value]]
    def transform_decr_val_to_set(dec_expr):
        [_, expr, value] = dec_expr
        return ["set", expr, ["-", expr, value]]


class Environment:
    def __init__(
        self,
        record,
        parent=None,
    ):
        if record is None:
            record = {}
        self.record = record
        self.parent = parent

    # Define a new variable
    def define(self, name, value):
        self.record[name] = value
        return value

    # Assign a new variable
    def assign(self, name, value):
        self.resolve(name).record[name] = value
        return value

    # Get the value of a variable
    def lookup(self, name):
        return self.resolve(name).record[name]

    # Get the environment in which a variable is defined
    def resolve(self, name):
        if name in self.record.keys():
            return self
        if self.parent is None:  # parent == None means we are in the global_env
            raise Exception(f"Variable not defined: {name}")
        return self.parent.resolve(name)


global_environment = Environment(
    {
        "null": None,
        "true": True,
        "false": False,
        "VERSION": VERSION_INFO,
        "+": lambda *args: operator.pos(args[0])
        if len(args) == 1
        else operator.add(args[0], args[1]),
        "*": operator.mul,
        "-": lambda *args: operator.neg(args[0])
        if len(args) == 1
        else operator.sub(args[0], args[1]),
        "/": operator.truediv,
        "//": operator.floordiv,
        "%": operator.mod,
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
        "=": operator.eq,
        "eof": lambda arg: arg is EOF,
    }
)


class Tea:
    # GLOBAL ENVIRONMENT
    def __init__(self, global_env=global_environment):
        self.global_env = global_env
        self.transformer = Transformer()

    def _output(self, expr):
        """Convert expression back to s-expression."""

        if not isinstance(expr, list):
            return str(expr)
        else:
            return '[' + ' '.join(map(self._output, expr)) + ']'

    # Compute an expression -> cmp
    def cmp(self, raw_expr: str):
        return self._output(
            self._eval_body(Parser.parse(f"[begin {raw_expr}]"), self.global_env)
        )

    def _eval(self, expr, env):
        if env is None:
            env = self.global_env

        # VAR LOOKUP
        if isinstance(expr, str):
            return env.lookup(expr)

        if isinstance(expr, int | float):
            return expr

        if isinstance(expr, list):
            # Quoted text
            if expr[0] == "quote":
                [_, string] = expr
                return string
            # BLOCKS
            if expr[0] == "begin":
                block_env = Environment({}, env)
                return self._eval_block(expr, block_env)

            # VAR DECLARATIONS
            elif expr[0] == "var":
                [_, name, value] = expr
                return env.define(name, self._eval(value, env))

            # VAR UPDATE
            elif expr[0] == "set":
                [_, ref, value] = expr
                # Set a property
                if ref[0] == "prop":
                    [_, instance, prop_name] = ref
                    instance_env = self._eval(instance, env)
                    return instance_env.define(prop_name, self._eval(value, env))
                # Set a var
                return env.assign(ref, self._eval(value, env))

            # IF EXPRESSION
            elif expr[0] == "if":
                [_, condition, consequent, alternate] = expr
                if self._eval(condition, env):
                    return self._eval(consequent, env)
                return self._eval(alternate, env)

            # WHILE LOOP
            elif expr[0] == "while":
                [_, condition, block] = expr
                result = None
                while self._eval(condition, env):
                    result = self._eval(block, env)
                return result

            # Function declaration
            # def is just syntactic sugar for lambda
            elif expr[0] == "def":
                # JIT-transpile to a var declaration
                var_expr = self.transformer.transform_def_to_var_lambda(expr)
                return self._eval(var_expr, env)

            elif expr[0] == "switch":
                if_expr = self.transformer.transform_switch_to_if(expr)
                return self._eval(if_expr, env)

            elif expr[0] == "for":
                while_expr = self.transformer.transform_for_to_while(expr)
                return self._eval(while_expr, env)

            elif expr[0] == "++":
                set_expr = self.transformer.transform_incr_to_set(expr)
                return self._eval(set_expr, env)

            elif expr[0] == "--":
                set_expr = self.transformer.transform_decr_to_set(expr)
                return self._eval(set_expr, env)

            elif expr[0] == "+=":
                set_expr = self.transformer.transform_incr_val_to_set(expr)
                return self._eval(set_expr, env)

            elif expr[0] == "-=":
                set_expr = self.transformer.transform_decr_val_to_set(expr)
                return self._eval(set_expr, env)

            # lambda function
            elif expr[0] == "lambda":
                [_, params, body] = expr
                return {
                    "params": params,
                    "body": body,
                    "env": env,  # Add this for Closure
                }

            # OOP CLASS
            elif expr[0] == "class":
                [_, name, parent, body] = expr

                # A class is just an environment!
                # A class store methods "def" and properties "prop"
                parent_env = self._eval(parent, env) or env
                class_env = Environment({}, parent_env)

                # Body is evaluated in the class environment
                self._eval_body(body, class_env)

                # A class can be accessed by name
                return env.define(name, class_env)

            elif expr[0] == "super":
                [_, class_name] = expr
                return self._eval(class_name, env).parent

            elif expr[0] == "new":  # [new <class name> <args> ...]
                class_env = self._eval(expr[1], env)

                # An instance of a class is an environment!
                instance_env = Environment({}, class_env)

                args = [self._eval(arg, env) for arg in expr[2:]]

                self._user_defined_function(
                    class_env.lookup("constructor"), [instance_env, *args]
                )

                return instance_env

            # Access to a property
            elif expr[0] == "prop":
                [_, instance, name] = expr
                instance_env = self._eval(instance, env)
                return instance_env.lookup(name)

            # Module declaration
            elif expr[0] == "module":
                [_, name, body] = expr
                module_env = Environment({}, env)
                _ = self._eval_body(body, module_env)
                return env.define(name, module_env)

            # Import module
            elif expr[0] == "import":
                [_, module_name] = expr
                # load module code
                file = f"{module_name}.{FILE_EXTENSION}"
                path = os.path.dirname(os.path.abspath(__file__))
                with open(os.path.join(path, "modules", file), mode="r") as f:
                    module_src = f.read()

                module_body = Parser.parse(f"[begin {module_src}]")
                module_expr = ["module", module_name, module_body]

                return self._eval(module_expr, self.global_env)

            # Function call
            else:
                fn = self._eval(expr[0], env)
                args = [self._eval(arg, env) for arg in expr[1:]]

                # Native Function
                if inspect.isfunction(fn) or inspect.isbuiltin(fn):
                    return fn(*args)

                # User-defined function
                return self._user_defined_function(fn, args)

        else:
            raise Exception(f"Unimplemented: {expr}")

    def _user_defined_function(self, fn, args):
        activation_record = {}

        for index, param in enumerate(fn["params"]):
            activation_record[param] = args[index]

        activation_env = Environment(
            activation_record,
            fn["env"],  # static scope
            # env, # dynamic scope
        )

        return self._eval_body(fn["body"], activation_env)

    def _eval_body(self, body, env):
        if body[0] == "begin":  # body is a block
            return self._eval_block(body, env)
        return self._eval(body, env)  # body is an expression

    def _eval_block(self, block, env):
        expressions = block[1:]
        result = None
        for expr in expressions:
            result = self._eval(expr, env)
        return result

    def repl(self, prompt="tea> "):
        """Prompt repl."""

        print(VERSION_INFO + "\n")

        while True:
            try:
                result = self.cmp(input(prompt))
                if result is not None:
                    print(result)
            except KeyboardInterrupt:
                print("\nNo more tea for now. Goodbye...\n")
                sys.exit()
            except Exception:
                print(
                    "Tea was spilled. Sorry.\nHere is the Python trace to help you:\n"
                )
                traceback.print_exc()


def load(filename):
    """
    Load a program in filename, execute it, and start the repl. If an error occurs,
    execution stops, and we are left in the repl. This function supports
    multi-line code by merging lines until the parentheses match.
    """
    print(f"Loading and executing {filename}")  # load module code
    file = f"{filename}"
    path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(path, file), mode="r") as f:
        program = f.readlines()

    rps = running_paren_sums(program)
    full_line = ""

    tea = Tea()
    tea.repl()
    for paren_sum, program_line in zip(rps, program):
        program_line = program_line.strip()
        full_line += program_line + " "
        if paren_sum == 0 and full_line.strip() != "":
            try:
                val = tea.cmp(full_line)
                if val is not None:
                    print(val)
            except Exception:
                print(f"\nThe line in which the error occurred:\n{full_line}")
                break
            full_line = ""
    tea.repl()


def running_paren_sums(program):
    """
    Map the lines in the list program to a list whose entries contain
    a running sum of the per-line difference between '[' and the number of ']'.
    """

    count_open_parens = lambda line: line.count("[") - line.count("]")
    paren_counts = list(map(count_open_parens, program))
    rps = []
    total = 0
    for paren_count in paren_counts:
        total += paren_count
        rps.append(total)
    return rps


if __name__ == "__main__":
    if len(sys.argv) > 1:
        load(sys.argv[1])
    else:
        tea = Tea()
        tea.repl()
