"""Core functionality of the unification engine.

The core does not make any assumptions about what concrete types can be unified.

Primarily, it provides the unify function, which unifies two terms and updates the substitution.

The behavior of unify can be extended by registering handlers for new types using the following decorators:

    1. @unify_dispatch.register, for unification handlers
    2. @occurs_dispatch.register, for occurs check handlers
"""

from functools import singledispatch
import typing


class Mismatch(Exception):
    """Two terms could not be matched"""


class Cycle(Exception):
    """Unification would result in a cycle"""


Term = typing.Any
Substitution = typing.Dict


def unify(u: Term, v: Term, s: Substitution) -> Substitution:
    """Unify two terms subject to a substitution, and return the resulting substitution."""
    u = walk(u, s)
    v = walk(v, s)

    if u == v:
        return s

    return unify_dispatch(u, v, s)


def walk(v: Term, s: Substitution) -> Term:
    """Recursively look up a term in the substitution."""
    try:
        a = s[v]
    except KeyError:
        return v
    except TypeError:
        return v
    else:
        return walk(a, s)


def walk_star(v: Term, s: Substitution) -> Term:
    """Recursively look up a term and its subterms in the substitution."""
    v = walk(v, s)
    return walk_dispatch(v, s)


def occurs(x: Term, v: Term, s: Substitution) -> bool:
    """Test if a variable occurs in a term, subject to a substitution"""
    v = walk(v, s)
    return occurs_dispatch(v, x, s)


def extend_substitution(x: Term, v: Term, s: Substitution) -> Substitution:
    """Extend a substitution by associating a term with a variable.
    If this would result in a cycle, the Cycle exception is thrown."""
    if occurs(x, v, s):
        raise Cycle(x, v, s)
    return s | {x: v}


def unify_dispatch(u: Term, v: Term, s: Substitution) -> Substitution:
    """Unify two walked terms by dispatching to the appropriate handler.
    Use the unifier decorator to register new handlers."""
    for predicate, handler in unify_handlers[::-1]:
        if predicate(u, v):
            return handler(u, v, s)
    raise Mismatch(u, v, s)


unify_handlers = []


@singledispatch
def occurs_dispatch(_v: Term, _x: Term, _s: Substitution) -> bool:
    """Test if x occurs in v given s. Dispatches to the appropriate handler based on v's type."""
    return False


@singledispatch
def walk_dispatch(v: Term, _s: Substitution) -> bool:
    """Test if x occurs in v given s. Dispatches to the appropriate handler based on v's type."""
    return v


def unifier(
    predicate: typing.Optional[typing.Callable[[Term, Term], bool]] = None,
    swap: bool = False,
):
    """Decorate a function to declare it as a unification handler.

    If predicate can be a function that, given two terms determines if the handler is applicable.
    If predicate is omitted, the handler is dispatched based on the types of the first two arguments.

    If swap is set to true, the handler is also registered for the first two arguments swapped.
    """

    def decorator(handler):
        unify_handlers.append((predicate, handler))
        return handler

    def annotation_unifier(handler):
        types = tuple(handler.__annotations__.values())
        t1, t2 = types[:2]

        def pred(a, b):
            return is_instance(a, t1) and is_instance(b, t2)

        unify_handlers.append((pred, handler))

        if swap:
            unify_handlers.append((swap_args(pred), swap_args(handler)))

        return handler

    if predicate is None:
        return annotation_unifier
    else:
        return decorator


unify_dispatch.register = unifier


def is_instance(obj: typing.Any, typ: typing.Type) -> bool:
    """Test if object is an instance of given type. Supports some additional types compared to the builtin."""
    if typ == typing.Any:
        return True
    return isinstance(obj, typ)


def swap_args(func):
    """Transform a function to swap its first two arguments"""

    def swap(a, b, *args, **kwargs):
        return func(b, a, *args, **kwargs)

    return swap
