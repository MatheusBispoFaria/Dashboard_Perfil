"""Cálculos estatísticos usados nos indicadores e gráficos."""

import math

CONFIDENCE_Z = {"90": 1.645, "95": 1.960, "99": 2.576}


def proportion_interval(successes, total, confidence):
    """Retorna os limites percentuais do intervalo normal de uma proporção."""
    if total == 0:
        return 0, 0

    proportion = successes / total
    error = CONFIDENCE_Z[confidence] * math.sqrt(
        proportion * (1 - proportion) / total
    )
    return max(0, proportion - error) * 100, min(1, proportion + error) * 100
