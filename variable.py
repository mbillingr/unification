from core import occurs_dispatch, unify_dispatch, extend_substitution
from typing import Any


class Var:
    def __repr__(self):
        return f"<Var @ {hex(id(self) & 0xFFFFFF)[2:]}>"


@unify_dispatch.register(swap=True)
def unify_variable(u: Var, v: Any, s):
    return extend_substitution(u, v, s)


@occurs_dispatch.register
def occurs_variable(v: Var, x, s):
    return v == x
