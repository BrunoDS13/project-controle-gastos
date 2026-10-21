import pytest

from app import criar_app


@pytest.fixture
def client(tmp_path):
    app = criar_app(tmp_path / "teste.db")
    app.config["TESTING"] = True
    return app.test_client()


def test_pagina_inicial_abre(client):
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert "Controle de Gastos" in resposta.get_data(as_text=True)


def test_adicionar_e_aparecer_na_lista(client):
    form = {"descricao": "Mercado", "valor": "150,50", "categoria": "alimentação", "data": "2026-10-05"}
    resposta = client.post("/adicionar", data=form, follow_redirects=True)
    html = resposta.get_data(as_text=True)
    assert "Gasto adicionado!" in html
    assert "Mercado" in html
    assert "150.50" in html


def test_valor_invalido_mostra_erro(client):
    form = {"descricao": "X", "valor": "abc", "categoria": "outros", "data": "2026-10-05"}
    html = client.post("/adicionar", data=form, follow_redirects=True).get_data(as_text=True)
    assert "Preencha" in html


def test_remover(client):
    form = {"descricao": "Cinema", "valor": "40", "categoria": "lazer", "data": "2026-10-07"}
    client.post("/adicionar", data=form)
    html = client.post("/remover/1", data={"mes": "2026-10"}, follow_redirects=True).get_data(as_text=True)
    assert "Gasto removido." in html


def test_exportar_csv(client):
    form = {"descricao": "Mercado", "valor": "150,50", "categoria": "alimentação", "data": "2026-10-05"}
    client.post("/adicionar", data=form)
    resposta = client.get("/exportar?mes=2026-10")
    assert resposta.mimetype == "text/csv"
    assert "attachment" in resposta.headers["Content-Disposition"]
    linhas = resposta.get_data(as_text=True).splitlines()
    assert linhas[0] == "data,descricao,categoria,valor"
    assert linhas[1] == "2026-10-05,Mercado,alimentação,150.50"


def _adicionar(client, valor, data):
    client.post("/adicionar", data={"descricao": "Gasto", "valor": valor, "categoria": "outros", "data": data})


def test_comparacao_com_mes_anterior(client):
    _adicionar(client, "100", "2026-09-10")
    _adicionar(client, "150", "2026-10-10")
    html = client.get("/?mes=2026-10").get_data(as_text=True)
    assert "2026-09: R$ 100.00" in html
    assert "50.0%" in html
    assert "a mais" in html


def test_comparacao_sem_mes_anterior(client):
    _adicionar(client, "150", "2026-10-10")
    html = client.get("/?mes=2026-10").get_data(as_text=True)
    assert "Sem gastos em 2026-09" in html
