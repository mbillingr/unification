from unittest.mock import Mock, patch
import pytest
from core import extend_substitution, occurs, unify, walk, Cycle, Mismatch


def test_walk_returns_term_if_not_in_substitution():
    assert walk("foo", {}) == "foo"


def test_walk_returns_substituted_term():
    assert walk("foo", {"foo": "bar"}) == "bar"


def test_walk_follows_multiple_substitutions():
    assert walk("foo", {"foo": "bar", "bar": "baz"}) == "baz"


def test_unifying_the_same_value_does_not_create_an_association():
    assert unify("x", "x", {}) == {}


def test_unifying_the_same_value_indirectly_does_not_create_an_association():
    sub = {"y": "x"}
    assert unify("x", "y", sub) == sub

    sub = {"x": "y"}
    assert unify("x", "y", sub) == sub


@patch("core.unify_dispatch")
def test_unify_returns_value_from_dispatch(unify_dispatch):
    s = unify("u", "v", {})
    assert s == unify_dispatch.return_value
    unify_dispatch.assert_called_once_with("u", "v", {})


@patch("core.unify_dispatch")
def test_unify_walks_terms(unify_dispatch):
    subs = {"u": Mock(), "v": Mock()}
    unify("u", "v", subs)
    unify_dispatch.assert_called_once_with(subs["u"], subs["v"], subs)


@patch("core.occurs_dispatch")
def test_occurs_returns_value_from_dispatch(occurs_dispatch):
    s = occurs("x", "v", {})
    assert s == occurs_dispatch.return_value
    occurs_dispatch.assert_called_once_with("v", "x", {})


@patch("core.occurs_dispatch")
def test_occurs_walks_right_hand_term(occurs_dispatch):
    subs = {"x": Mock(), "v": Mock()}
    occurs("x", "v", subs)
    occurs_dispatch.assert_called_once_with(subs["v"], "x", subs)


def test_extend_substitution_associates_two_terms():
    assert extend_substitution("foo", "bar", {}) == {"foo": "bar"}


def test_extend_substitution_preserves_existing_associations():
    assert extend_substitution("foo", "bar", {"x": "y"}) == {"foo": "bar", "x": "y"}


@patch("core.occurs")
def test_extend_substitution_raises_cycle_if_x_occurs_in_v(occurs):
    occurs.return_value = True
    with pytest.raises(Cycle):
        extend_substitution("foo", "bar", {})
