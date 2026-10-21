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


def test_sem_previsao_nos_primeiros_dias():
    assert prever_total(300, "2026-09", date(2026, 9, 3)) is None


def test_previsao_a_partir_do_setimo_dia():
    assert prever_total(70, "2026-09", date(2026, 9, 7)) is not None


def test_poucos_dados_so_vale_para_o_mes_em_andamento():
    from gastos.previsao import poucos_dados

    assert poucos_dados("2026-09", date(2026, 9, 3)) is True
    assert poucos_dados("2026-09", date(2026, 9, 7)) is False
    assert poucos_dados("2026-08", date(2026, 9, 3)) is False
