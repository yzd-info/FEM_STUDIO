"""M3.1: parse ODE text into SymPy expressions (docs/MATH_SPEC.md §9).

Valid cases cross-check against docs/BENCHMARKS.md §2's free-text table and
against expressions built directly with SymPy (ground truth independent of
the parser). Invalid cases cover grammar violations and injection attempts
that the restricted namespace must reject without ever calling `eval`.
"""

import pytest
import sympy as sp

from fem1d.parsing import ParseError, X, parse_equation

_U = sp.Function("u")(X)


def _residual_equals(parsed_residual: sp.Expr, expected: sp.Expr) -> bool:
    return sp.simplify(sp.expand(parsed_residual - expected)) == 0


# --- valid inputs: docs/BENCHMARKS.md §2 -----------------------------------


def test_b1_minus_u_double_prime_equals_one() -> None:
    parsed = parse_equation("-u'' = 1")
    expected = -sp.Derivative(_U, X, 2) - 1
    assert _residual_equals(parsed.residual, expected)


def test_b3_product_rule_divergence_form_expands() -> None:
    parsed = parse_equation("-((1+x)*u')' = 1")
    expected = -sp.Derivative((1 + X) * sp.Derivative(_U, X), X).doit() - 1
    assert _residual_equals(parsed.residual, expected)


def test_b3_prime_and_expanded_forms_agree() -> None:
    prime_form = parse_equation("-((1+x)*u')' = 1")
    expanded_form = parse_equation("-(1+x)*u'' - u' = 1")
    assert _residual_equals(prime_form.residual, expanded_form.residual)


def test_b4_u_double_prime_minus_u_equals_minus_x() -> None:
    parsed = parse_equation("u'' - u = -x")
    expected = sp.Derivative(_U, X, 2) - _U - (-X)
    assert _residual_equals(parsed.residual, expected)


def test_b5_decimal_coefficient_and_first_derivative() -> None:
    parsed = parse_equation("-0.05*u'' + u' = 0")
    expected = -sp.Float(0.05) * sp.Derivative(_U, X, 2) + sp.Derivative(_U, X)
    assert _residual_equals(parsed.residual, expected)


def test_b8_caret_power_and_negative_coefficient() -> None:
    parsed = parse_equation("u'' + 100*u = 0")
    expected = sp.Derivative(_U, X, 2) + 100 * _U
    assert _residual_equals(parsed.residual, expected)


def test_b9_diff_notation_with_exp_function() -> None:
    parsed = parse_equation("-diff(exp(x)*diff(u,x),x) = exp(x)*(1+2*x)")
    expected = -sp.diff(sp.exp(X) * sp.diff(_U, X), X) - sp.exp(X) * (1 + 2 * X)
    assert _residual_equals(parsed.residual, expected)


def test_b10_mixed_derivative_orders_and_function() -> None:
    parsed = parse_equation("-u'' + u' + 2*u = 2*exp(x)")
    expected = -sp.Derivative(_U, X, 2) + sp.Derivative(_U, X) + 2 * _U - 2 * sp.exp(X)
    assert _residual_equals(parsed.residual, expected)


def test_m4_y_alias_and_caret_power() -> None:
    parsed = parse_equation("y'' = 12*x^2")
    expected = sp.Derivative(_U, X, 2) - 12 * X**2
    assert _residual_equals(parsed.residual, expected)


# --- valid inputs: grammar coverage beyond the benchmark table -------------


def test_missing_equals_sign_defaults_rhs_to_zero() -> None:
    parsed = parse_equation("u''")
    assert parsed.rhs == 0


def test_pi_and_e_constants_resolve() -> None:
    parsed = parse_equation("u = pi + E")
    assert _residual_equals(parsed.residual, _U - sp.pi - sp.E)


@pytest.mark.parametrize(
    "name,fn",
    [
        ("sin", sp.sin),
        ("cos", sp.cos),
        ("tan", sp.tan),
        ("log", sp.log),
        ("sqrt", sp.sqrt),
        ("sinh", sp.sinh),
        ("cosh", sp.cosh),
        ("tanh", sp.tanh),
    ],
)
def test_whitelisted_function_resolves(name: str, fn) -> None:  # type: ignore[no-untyped-def]
    parsed = parse_equation(f"u = {name}(x)")
    assert _residual_equals(parsed.residual, _U - fn(X))


def test_whitespace_is_insignificant() -> None:
    tight = parse_equation("-u''=1")
    spaced = parse_equation("  -  u ''  =  1  ")
    assert _residual_equals(tight.residual, spaced.residual)


def test_double_prime_via_repeated_single_primes_text() -> None:
    # same mathematical content as B1, written with `diff` instead of `''`
    parsed = parse_equation("-diff(u,x,2) = 1")
    expected = -sp.Derivative(_U, X, 2) - 1
    assert _residual_equals(parsed.residual, expected)


def test_triple_prime_order_is_counted() -> None:
    parsed = parse_equation("u''' = 0")
    assert parsed.lhs == sp.Derivative(_U, X, 3)


def test_unknown_bare_symbol_becomes_free_symbol_not_a_parse_error() -> None:
    # docs/BENCHMARKS.md §5: `-u'' = k` is rejected by the *scope gate* (M3.3)
    # as UNKNOWN_SYMBOL, not by the parser -- M3.1 must stay permissive here.
    parsed = parse_equation("-u'' = k")
    assert sp.Symbol("k") in parsed.rhs.free_symbols


# --- invalid inputs: grammar violations ------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "u'' = 1 = 2",
        "-(u'' = 1",
        "-((1+x)*u')) = 1",
        "'u = 1",
        "u'' = 1; import os",
        "__import__('os').system('echo hi')",
        "u'' = os.system('echo hi')",
        "u'' = 1 # comment",
        "u'' = {1: 2}",
        "u'' = [1, 2]",
        "u'' = 1 @ 2",
        "lambda_ = 1",
        "u'' = 1 if True else 0",
        "u'' == 1",
        "u'' = 1 and 1",
        "k$ = 1",
        "u'' = 1``",
        "2 +* 3",
        "u'' = 1\nu' = 2",
    ],
)
def test_invalid_grammar_is_rejected(text: str) -> None:
    with pytest.raises(ParseError):
        parse_equation(text)


def test_error_message_is_turkish() -> None:
    with pytest.raises(ParseError, match="boş olamaz"):
        parse_equation("")


def test_unmatched_parens_message_is_turkish() -> None:
    # the prime's matching "(" is searched for and never found -> our own
    # message fires directly, before the text ever reaches sympy's parser.
    with pytest.raises(ParseError, match="[Pp]aranez|eşleşmiyor"):
        parse_equation(")' = 1")
