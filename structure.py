from abc import ABC, abstractmethod
from core import Substitution, occurs_dispatch, unify_dispatch


class Structure(ABC):
    @abstractmethod
    def occurs(self, x: "Structure", s: Substitution) -> bool:
        """Test if x occurs in this structure."""

    @abstractmethod
    def unify(self, other: "Structure", s: Substitution) -> Substitution:
        """Unify this with another structure."""


@unify_dispatch.register()
def unify_structure(u: Structure, v: Structure, s):
    return u.unify(v, s)


@occurs_dispatch.register
def occurs_structure(v: Structure, x, s):
    return v.occurs(x, s)
