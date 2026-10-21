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


def test_gastos_fixos_nao_entram_no_ritmo():
    # R$ 900 de aluguel (fixo) + R$ 100 variáveis em 10 dias, mês de 30 dias
    # variáveis: 100 / 10 * 30 = 300  ->  previsão = 300 + 900 = 1200
    assert prever_total(1000, "2026-09", date(2026, 9, 10), total_fixo=900) == 1200


def test_so_gastos_fixos_a_previsao_e_o_proprio_valor():
    assert prever_total(900, "2026-09", date(2026, 9, 10), total_fixo=900) == 900
