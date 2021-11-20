from core import unify, occurs
from variable import Var


def test_different_variables_dont_occur_in_each_other():
    assert not occurs(Var(), Var(), {})


def test_same_variable_occurs_in_itself():
    var = Var()
    assert occurs(var, var, {})


def test_variable_occurs_in_substitution():
    a = Var()
    b = Var()
    assert occurs(a, b, {b: a})


def test_variable_occurs_in_longer_substitution_chain():
    a = Var()
    b = Var()
    c = Var()
    assert occurs(a, b, {b: c, c: a})


def test_unifying_two_variables_extends_the_substitution():
    a, b = Var(), Var()
    s = unify(a, b, {})
    assert s == {a: b} or s == {b: a}


def test_unifying_variable_with_itself_does_not_extend_the_substitution():
    var = Var()
    s = unify(var, var, {})
    assert s == {}


def test_unifying_a_variable_with_a_value_associates_the_variable_with_the_value():
    var = Var()

    s = unify(var, 42, {})
    assert s == {var: 42}

    s = unify(42, var, {})
    assert s == {var: 42}
