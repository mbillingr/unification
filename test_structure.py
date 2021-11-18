from unittest.mock import Mock
import pytest
from core import unify, occurs
from structure import Structure


def test_occurs_is_not_called_on_first_argument():
    spy = SpyStructure()
    occ = occurs(spy, "foo", {})
    spy.occurs_.assert_not_called()


def test_occurs_is_called_on_second_argument():
    spy = SpyStructure()
    occ = occurs("foo", spy, {})
    assert occ == spy.occurs_.return_value
    spy.occurs_.assert_called_once_with("foo", {})


def test_unify_is_called_on_either_argument_and_gets_passed_the_other():
    a, b = SpyStructure(), SpyStructure()
    s = unify(a, b, {})
    if s == a.unify_.return_value:
        a.unify_.assert_called_once_with(b, {})
    elif s == b.unify_.return_value:
        b.unify_.assert_called_once_with(a, {})
    else:
        pytest.fail("did not return unification of one of the terms")


class SpyStructure(Structure):
    def __init__(self):
        self.occurs_ = Mock()
        self.unify_ = Mock()

    def occurs(self, x, s):
        return self.occurs_(x, s)

    def unify(self, other, s):
        return self.unify_(other, s)