from gastos.periodos import mes_anterior, ultimos_meses


def test_mes_anterior_comum():
    assert mes_anterior("2026-10") == "2026-09"


def test_mes_anterior_virada_de_ano():
    assert mes_anterior("2026-01") == "2025-12"


def test_ultimos_meses_cruza_o_ano():
    assert ultimos_meses("2026-02", 4) == ["2025-11", "2025-12", "2026-01", "2026-02"]


def test_mes_seguinte_comum_e_virada_de_ano():
    from gastos.periodos import mes_seguinte

    assert mes_seguinte("2026-09") == "2026-10"
    assert mes_seguinte("2026-12") == "2027-01"


def test_nome_do_mes():
    from gastos.periodos import nome_do_mes

    assert nome_do_mes("2026-10") == "outubro de 2026"
    assert nome_do_mes("2026-03") == "março de 2026"


def test_mes_valido():
    from gastos.periodos import mes_valido

    assert mes_valido("2026-10") is True
    for ruim in ["", None, "abc", "2026-13", "2026-00", "2026-1", "26-10", "2026/10", "2026-1a"]:
        assert mes_valido(ruim) is False, ruim
