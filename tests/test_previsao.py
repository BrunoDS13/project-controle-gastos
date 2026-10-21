from datetime import date

from gastos.previsao import prever_total


def test_previsao_pelo_ritmo_atual():
    # R$ 500 em 10 dias, mês de 30 dias -> R$ 1500
    assert prever_total(500, "2026-09", date(2026, 9, 10)) == 1500


def test_previsao_no_ultimo_dia_e_o_proprio_total():
    assert prever_total(900, "2026-09", date(2026, 9, 30)) == 900


def test_sem_previsao_para_mes_passado():
    assert prever_total(500, "2026-08", date(2026, 9, 10)) is None


def test_sem_previsao_para_mes_futuro():
    assert prever_total(500, "2026-10", date(2026, 9, 10)) is None


def test_sem_previsao_sem_gastos():
    assert prever_total(0, "2026-09", date(2026, 9, 10)) is None
