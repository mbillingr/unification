from abc import ABC, abstractmethod
from core import occurs_dispatch, unify_dispatch, extend_substitution, Term, Mismatch
from variable import Var
from typing import Any, Optional


# For now, assume constraints can't contain variables.
# We can say things like >0 or >10 & <20, but not <X.


class Constraint(ABC):
    @abstractmethod
    def check(self, value: Term) -> bool:
        pass

    @abstractmethod
    def combine(self, other) -> Optional["Constraint"]:
        pass


@unify_dispatch.register(swap=True)
def unify_constraints(u: Constraint, v: Any, s):
    if u.check(v):
        return s
    raise Mismatch(u, v)


@unify_dispatch.register()
def unify_constraints(u: Constraint, v: Var, s):
    # It's tricky...
    #   after walking, a variable associated with a constraint is replaced by the constraint.
    #   so how can we update the constraint here?
    raise NotImplementedError()


@unify_dispatch.register()
def unify_constraints(u: Constraint, v: Constraint, s):
    if not u.combine(v):
        raise Mismatch(u, v)
    return s


@occurs_dispatch.register
def occurs_constraint(v: Constraint, x, s):
    return False
