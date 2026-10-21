import pytest

from gastos import db


@pytest.fixture
def conexao():
    return db.conectar(":memory:")


def test_adicionar_e_listar(conexao):
    novo_id = db.adicionar_gasto(conexao, "Mercado", 150.0, "alimentacao", "2026-10-05")
    gastos = db.listar_gastos(conexao)
    assert len(gastos) == 1
    assert gastos[0]["id"] == novo_id
    assert gastos[0]["descricao"] == "Mercado"


def test_filtrar_por_categoria(conexao):
    db.adicionar_gasto(conexao, "Mercado", 150.0, "alimentacao", "2026-10-05")
    db.adicionar_gasto(conexao, "Ônibus", 20.0, "transporte", "2026-10-06")
    gastos = db.listar_gastos(conexao, categoria="transporte")
    assert [g["descricao"] for g in gastos] == ["Ônibus"]


def test_remover(conexao):
    novo_id = db.adicionar_gasto(conexao, "Cinema", 40.0, "lazer", "2026-10-07")
    assert db.remover_gasto(conexao, novo_id) is True
    assert db.remover_gasto(conexao, novo_id) is False


def test_total_por_categoria(conexao):
    db.adicionar_gasto(conexao, "Mercado", 100.0, "alimentacao", "2026-10-05")
    db.adicionar_gasto(conexao, "Padaria", 50.0, "alimentacao", "2026-10-08")
    db.adicionar_gasto(conexao, "Ônibus", 20.0, "transporte", "2026-09-30")
    totais = db.total_por_categoria(conexao, mes="2026-10")
    assert [tuple(t) for t in totais] == [("alimentacao", 150.0)]


def test_total_do_mes(conexao):
    db.adicionar_gasto(conexao, "Mercado", 100.0, "alimentacao", "2026-10-05")
    db.adicionar_gasto(conexao, "Ônibus", 20.0, "transporte", "2026-10-06")
    db.adicionar_gasto(conexao, "Cinema", 30.0, "lazer", "2026-09-10")
    assert db.total_do_mes(conexao, "2026-10") == 120.0
    assert db.total_do_mes(conexao, "2026-08") == 0


def test_total_por_mes(conexao):
    db.adicionar_gasto(conexao, "Mercado", 100.0, "alimentacao", "2026-10-05")
    db.adicionar_gasto(conexao, "Cinema", 30.0, "lazer", "2026-09-10")
    db.adicionar_gasto(conexao, "Padaria", 15.0, "alimentacao", "2026-09-12")
    assert db.total_por_mes(conexao) == {"2026-10": 100.0, "2026-09": 45.0}


def test_meta_sem_definir_devolve_none(conexao):
    assert db.obter_meta(conexao, "2026-10") is None


def test_definir_e_trocar_meta(conexao):
    db.definir_meta(conexao, "2026-10", 1500.0)
    assert db.obter_meta(conexao, "2026-10") == 1500.0
    db.definir_meta(conexao, "2026-10", 1800.0)
    assert db.obter_meta(conexao, "2026-10") == 1800.0


def test_meta_vale_para_meses_seguintes(conexao):
    db.definir_meta(conexao, "2026-08", 1500.0)
    assert db.obter_meta(conexao, "2026-10") == 1500.0
    assert db.obter_meta(conexao, "2026-07") is None
    db.definir_meta(conexao, "2026-10", 2000.0)
    assert db.obter_meta(conexao, "2026-09") == 1500.0
    assert db.obter_meta(conexao, "2026-11") == 2000.0


def test_gasto_fixo_e_total_fixo(conexao):
    db.adicionar_gasto(conexao, "Aluguel", 900.0, "moradia", "2026-10-05", fixo=True)
    db.adicionar_gasto(conexao, "Mercado", 100.0, "alimentacao", "2026-10-06")
    assert db.total_fixo_do_mes(conexao, "2026-10") == 900.0
    assert db.total_do_mes(conexao, "2026-10") == 1000.0
    assert [bool(g["fixo"]) for g in db.listar_gastos(conexao)] == [False, True]


def test_banco_antigo_sem_coluna_fixo_e_migrado(tmp_path):
    import sqlite3

    caminho = tmp_path / "antigo.db"
    antigo = sqlite3.connect(caminho)
    antigo.execute(
        "CREATE TABLE gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT NOT NULL, "
        "valor REAL NOT NULL, categoria TEXT NOT NULL, data TEXT NOT NULL)"
    )
    antigo.execute("INSERT INTO gastos (descricao, valor, categoria, data) VALUES ('Velho', 10, 'outros', '2026-01-01')")
    antigo.commit()
    antigo.close()

    conexao = db.conectar(caminho)
    gasto = db.listar_gastos(conexao)[0]
    assert gasto["descricao"] == "Velho"
    assert gasto["fixo"] == 0
