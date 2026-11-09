"""Parse ODE text into SymPy expressions (docs/MATH_SPEC.md §9; step M3.1).

No `eval`: the text is first rewritten (`'` and `diff(u, x, k)` derivative
notation become explicit `Derivative(...)` calls, `^` becomes `**`, bare `u`/`y`
become `u(x)`) and then handed to `sympy.parsing.sympy_parser.parse_expr` with
a restricted namespace -- only the functions/constants of MATH_SPEC §9 resolve;
anything else becomes a free SymPy `Symbol` (semantic scope checks, including
`UNKNOWN_SYMBOL`, are step M3.3's job, not this one's).
"""

import keyword
import re
from dataclasses import dataclass

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

X = sp.Symbol("x")
_U = sp.Function("u")

_ALLOWED_CHARS = re.compile(r"^[0-9A-Za-z+\-*/^().,.'=\s]*$")
_WORD = re.compile(r"[A-Za-z]+")
_BARE_U_OR_Y = re.compile(r"\b[uy]\b(?!\()")

_FUNCTION_NAMES = ("sin", "cos", "tan", "exp", "log", "sqrt", "sinh", "cosh", "tanh")
_NAMESPACE: dict[str, object] = {name: getattr(sp, name) for name in _FUNCTION_NAMES}
_NAMESPACE.update(
    {
        "x": X,
        "u": _U,
        "pi": sp.pi,
        "E": sp.E,
        "diff": sp.diff,
        "Derivative": sp.Derivative,
        # auto_number/auto_symbol (sympy_parser's standard transformations)
        # rewrite literals and bare names into calls to these; without them
        # in the namespace every number or unknown symbol raises NameError.
        "Integer": sp.Integer,
        "Float": sp.Float,
        "Rational": sp.Rational,
        "Symbol": sp.Symbol,
    }
)


class ParseError(ValueError):
    """The input text does not follow the ODE grammar (docs/MATH_SPEC.md §9)."""


@dataclass(frozen=True)
class ParsedEquation:
    """`lhs = rhs`, derivatives already expanded (`Derivative.doit()`)."""

    lhs: sp.Expr
    rhs: sp.Expr

    @property
    def residual(self) -> sp.Expr:
        """`lhs - rhs`, expanded; the equation holds iff this is identically 0."""
        return sp.expand(self.lhs - self.rhs)


def _expand_primes(text: str) -> str:
    """Rewrite `u''`, `u'` and `(expr*u')'` into `Derivative(...)` calls.

    Processes the leftmost `'` first, so an inner derivative (e.g. the `u'`
    inside `(expr*u')'`) is always rewritten before the outer one -- which is
    exactly the order needed for the outer `Derivative(..., x).doit()` to
    later expand correctly via SymPy's own product rule.
    """
    while "'" in text:
        j = text.index("'")
        if j == 0:
            raise ParseError("' işareti bir ifadeden önce gelemez.")
        k = j - 1
        while k >= 0 and text[k].isspace():
            k -= 1
        if k < 0:
            raise ParseError("' işareti bir ifadeden önce gelemez.")
        if text[k] == ")":
            depth = 0
            i = k
            while i >= 0:
                if text[i] == ")":
                    depth += 1
                elif text[i] == "(":
                    depth -= 1
                    if depth == 0:
                        break
                i -= 1
            if depth != 0:
                raise ParseError("Parantezler eşleşmiyor.")
            start = i
            while start - 1 >= 0 and (text[start - 1].isalnum() or text[start - 1] == "_"):
                start -= 1
        elif text[k].isalnum() or text[k] == "_":
            i = k
            while i >= 0 and (text[i].isalnum() or text[i] == "_"):
                i -= 1
            start = i + 1
        else:
            raise ParseError(f"' işareti geçersiz bir yerde: ...{text[max(0, j - 10) : j + 1]}")

        unit = text[start:j]
        order = 1
        while j + order < len(text) and text[j + order] == "'":
            order += 1
        replacement = f"Derivative({unit}, x, {order})" if order > 1 else f"Derivative({unit}, x)"
        text = text[:start] + replacement + text[j + order :]
    return text


def parse_equation(text: str) -> ParsedEquation:
    """Parse ODE text (docs/MATH_SPEC.md §9) into a `lhs = rhs` pair.

    Raises `ParseError` (Turkish message) on grammar violations. Symbols other
    than `x` that appear are kept as free SymPy symbols -- rejecting them as
    `UNKNOWN_SYMBOL` is the scope gate's job (M3.3), not this parser's.
    """
    if not text or not text.strip():
        raise ParseError("Girdi boş olamaz.")
    if not _ALLOWED_CHARS.match(text):
        raise ParseError(
            "Girdi yalnızca sayılar, x, u, y, izin verilen fonksiyonlar "
            "(sin cos tan exp log sqrt sinh cosh tanh), pi, E ve + - * / ^ ( ) , ' = "
            "içerebilir."
        )
    if text.count("=") > 1:
        raise ParseError("Girdi en fazla bir '=' işareti içerebilir.")
    for token in _WORD.findall(text):
        if keyword.iskeyword(token) or keyword.issoftkeyword(token):
            raise ParseError(f"'{token}' bu dilbilgisinin bir parçası değil (MATH_SPEC §9).")

    normalized = text.replace("^", "**")
    normalized = _BARE_U_OR_Y.sub("u(x)", normalized)
    normalized = _expand_primes(normalized)

    if "=" in normalized:
        lhs_text, rhs_text = normalized.split("=")
    else:
        lhs_text, rhs_text = normalized, "0"

    try:
        lhs = parse_expr(lhs_text, local_dict=_NAMESPACE, global_dict={}, evaluate=True)
        rhs = parse_expr(rhs_text, local_dict=_NAMESPACE, global_dict={}, evaluate=True)
    except ParseError:
        raise
    except Exception as exc:
        raise ParseError(f"Girdi ayrıştırılamadı: {exc}") from exc

    return ParsedEquation(lhs=sp.sympify(lhs).doit(), rhs=sp.sympify(rhs).doit())
