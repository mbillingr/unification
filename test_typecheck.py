from dataclasses import dataclass
from typing import Any, Type
import typing

from core import occurs, unify, walk_star
from variable import Var
from structure import Structure


class Pair(Structure):
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def occurs(self, x, s) -> bool:
        return occurs(x, self.car, s) or occurs(x, self.cdr, s)

    def unify(self, other, s):
        raise NotImplementedError()

    def walk_star(self, s):
        return Pair(walk_star(self.car, s), walk_star(self.cdr, s))

    def __repr__(self):
        return f"({self.car} . {self.cdr})"

    def __eq__(self, other):
        if not isinstance(other, Pair):
            return NotImplemented
        return self.car == other.car and self.cdr == other.cdr


class TypeChecker:
    def __init__(self):
        self.substitution = {}

    def eq(self, t1, t2):
        self.substitution = unify(t1, t2, self.substitution)

    def resolve(self, var):
        return walk_star(var, self.substitution)


class Function:
    def __init__(self, arity, code):
        self.arity = arity
        self.code = code
        self._signature = None

    def signature(self):
        if self._signature is None:
            args, ret = self.infer_signature()
            self._signature = (ret,) + tuple(args)

        mapping = {}

        vars = []
        for param in self._signature:
            try:
                var = mapping[param]
            except KeyError:
                var = Var()
                mapping[param] = var
            vars.append(var)

        ret = vars[0]
        params = vars[1:]
        return params, ret

    def infer_signature(self):
        tc = TypeChecker()

        args = tuple([Var() for _ in range(self.arity)])
        ret = Var()

        queue = [State(args, ret)]
        states = {}
        while queue:
            state = queue.pop()

            if state.ip in states:
                old_state = states[state.ip]
                assert len(state.stack) == len(old_state.stack)
                for a, b in zip(state.stack, old_state.stack):
                    tc.eq(a, b)
                continue

            states[state.ip] = state

            op = self.code[state.ip]
            next_states = op.typecheck(state, tc)
            queue.extend(next_states)

        args = [tc.resolve(a) for a in args]
        ret = tc.resolve(ret)
        return args, ret


@dataclass
class State:
    args: typing.Tuple
    retval: typing.Any
    ip: int = 0
    stack: typing.Tuple = ()

    def advance(self, offset=1):
        return State(self.args, self.retval, self.ip + offset, self.stack)

    def push(self, x):
        return State(self.args, self.retval, self.ip, self.stack + (x,))

    def pop(self):
        return self.stack[-1], State(self.args, self.retval, self.ip, self.stack[:-1])


@dataclass
class Const:
    value: Any

    def typecheck(self, state: State, tc: TypeChecker):
        yield state.push(type(self.value)).advance()


@dataclass
class Func:
    value: Function

    def typecheck(self, state: State, tc: TypeChecker):
        yield state.push(self.value).advance()


class Return:
    def typecheck(self, state: State, tc: TypeChecker):
        tc.eq(state.retval, state.stack[-1])
        return []


@dataclass
class Jump:
    offset: int

    def typecheck(self, state: State, tc: TypeChecker):
        yield state.advance(self.offset + 1)


@dataclass
class Branch:
    offset: int

    def typecheck(self, state: State, tc: TypeChecker):
        var, state = state.pop()
        tc.eq(var, bool)
        yield state.advance()
        yield state.advance(self.offset + 1)


@dataclass
class Arg:
    idx: int

    def typecheck(self, state: State, tc: TypeChecker):
        yield state.push(state.args[self.idx]).advance()


class Apply:
    def typecheck(self, state: State, tc: TypeChecker):
        func, state = state.pop()
        params, ret = func.signature()
        for prm in params:
            arg, state = state.pop()
            tc.eq(prm, arg)
        yield state.push(ret).advance()


class Cons:
    def typecheck(self, state: State, tc: TypeChecker):
        cdr, state = state.pop()
        car, state = state.pop()
        yield state.push(Pair(car, cdr)).advance()


def test_infer_constant_function():
    func = Function(0, [Const(42), Return()])
    args, ret = func.infer_signature()
    assert args == []
    assert ret == int


def test_infer_identity_function():
    func = Function(1, [Arg(0), Return()])
    args, ret = func.infer_signature()
    assert args == [ret]
    assert isinstance(ret, Var)


def test_infer_branch():
    select = Function(3, [Arg(0), Branch(2), Arg(1), Jump(1), Arg(2), Return()])
    args, ret = select.infer_signature()
    assert args == [bool, ret, ret]
    assert isinstance(ret, Var)


def test_infer_cons():
    select = Function(2, [Arg(0), Arg(1), Cons(), Return()])
    args, ret = select.infer_signature()
    assert args == [ret.car, ret.cdr]


def test_infer_application():
    identity = Function(1, [Arg(0), Return()])
    select = Function(0, [Const(42), Func(identity), Apply(), Return()])
    args, ret = select.infer_signature()
    assert args == []
    assert ret == int


def test_infer_application_with_different_types():
    """This fails for naive function signature handling (reuse of type variables over calls)"""
    identity = Function(1, [Arg(0), Return()])
    func = Function(
        0,
        [
            # apply identity to an integer type
            Const(42),
            Func(identity),
            Apply(),
            Const("foo"),
            # apply identity to a string type
            Func(identity),
            Apply(),
            # combine results
            Cons(),
            Return(),
        ],
    )
    args, ret = func.infer_signature()
    assert args == []
    assert ret == Pair(int, str)
