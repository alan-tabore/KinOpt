"""Render compact mathematical expressions for the selection guidance."""

from functools import lru_cache
from io import BytesIO

from matplotlib import rc_context
from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import math_to_image


@lru_cache(maxsize=64)
def render_equation_png(equation, color="#202020", font_size=13, dpi=180):
    """Return a transparent PNG rendered with Matplotlib's built-in mathtext.

    Mathtext provides stacked fractions and composed exponents without a
    system LaTeX installation. The cache avoids redrawing an equation whenever
    the user returns to a selection.
    """
    if not equation or not equation.strip():
        raise ValueError("An equation is required")

    expression = equation.strip()
    if not (expression.startswith("$") and expression.endswith("$")):
        expression = f"${expression}$"

    output = BytesIO()
    with rc_context({"savefig.transparent": True}):
        math_to_image(
            expression,
            output,
            prop=FontProperties(size=font_size),
            dpi=dpi,
            format="png",
            color=color,
        )
    return output.getvalue()
