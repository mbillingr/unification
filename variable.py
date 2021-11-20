from core import occurs_dispatch, unify_dispatch, extend_substitution
from typing import Any

from funny_id import hash_id


class Var:
    def __repr__(self):
        return f"<{hash_id(id(self), separator='-')}>"


@unify_dispatch.register(swap=True)
def unify_variable(u: Var, v: Any, s):
    return extend_substitution(u, v, s)


@occurs_dispatch.register
def occurs_variable(v: Var, x, s):
    return v == x
