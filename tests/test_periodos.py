from gastos.periodos import mes_anterior, ultimos_meses


def test_mes_anterior_comum():
    assert mes_anterior("2026-10") == "2026-09"


def test_mes_anterior_virada_de_ano():
    assert mes_anterior("2026-01") == "2025-12"


def test_ultimos_meses_cruza_o_ano():
    assert ultimos_meses("2026-02", 4) == ["2025-11", "2025-12", "2026-01", "2026-02"]
