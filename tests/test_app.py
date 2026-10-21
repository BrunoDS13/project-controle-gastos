from datetime import date

import pytest

from app import criar_app

HOJE = date(2026, 10, 21)


def criar_cliente(caminho, hoje=HOJE):
    app = criar_app(caminho, hoje=lambda: hoje)
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def client(tmp_path):
    return criar_cliente(tmp_path / "teste.db")


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
    assert linhas[0] == "data,descricao,categoria,valor,fixo"
    assert linhas[1] == "2026-10-05,Mercado,alimentação,150.50,nao"


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


def test_rota_do_grafico_devolve_png(client):
    _adicionar(client, "100", "2026-10-10")
    resposta = client.get("/grafico.png?mes=2026-10")
    assert resposta.mimetype == "image/png"
    assert resposta.data.startswith(b"\x89PNG")


def test_pagina_tem_botao_de_tema(client):
    html = client.get("/").get_data(as_text=True)
    assert 'id="tema"' in html
    assert "tema.js" in html


def test_definir_meta_e_ver_progresso(client):
    _adicionar(client, "800", "2026-10-10")
    client.post("/meta", data={"mes": "2026-10", "valor": "1000"})
    html = client.get("/?mes=2026-10").get_data(as_text=True)
    assert "Meta: R$ 1000.00" in html
    assert "80%" in html
    assert "Ainda dá para gastar R$ 200.00" in html


def test_meta_estourada(client):
    _adicionar(client, "1200", "2026-10-10")
    client.post("/meta", data={"mes": "2026-10", "valor": "1000"})
    html = client.get("/?mes=2026-10").get_data(as_text=True)
    assert "Você passou da meta em R$ 200.00" in html


def test_meta_invalida(client):
    html = client.post("/meta", data={"mes": "2026-10", "valor": "-5"}, follow_redirects=True).get_data(as_text=True)
    assert "Informe uma meta maior que zero." in html


def test_previsao_aparece_no_mes_atual(client):
    _adicionar(client, "100", "2026-10-10")
    html = client.get("/?mes=2026-10").get_data(as_text=True)
    assert "Previsão para o fim do mês" in html


def test_previsao_nao_aparece_em_mes_passado(client):
    _adicionar(client, "100", "2020-01-10")
    html = client.get("/?mes=2020-01").get_data(as_text=True)
    assert "Previsão para o fim do mês" not in html


def test_gasto_fixo_aparece_marcado(client):
    form = {"descricao": "Aluguel", "valor": "900", "categoria": "moradia", "data": "2026-10-05", "fixo": "on"}
    client.post("/adicionar", data=form)
    html = client.get("/?mes=2026-10").get_data(as_text=True)
    assert 'class="selo-fixo"' in html


def test_previsao_ignora_gasto_fixo_na_tela(client):
    client.post("/adicionar", data={"descricao": "Aluguel", "valor": "900", "categoria": "moradia", "data": "2026-10-05", "fixo": "on"})
    html = client.get("/?mes=2026-10").get_data(as_text=True)
    # só há gasto fixo: a previsão é o próprio valor, sem multiplicar pelo ritmo
    assert "R$ 900.00</strong>" in html


def test_tela_de_edicao_vem_preenchida(client):
    _adicionar(client, "150", "2026-10-05")
    html = client.get("/editar/1").get_data(as_text=True)
    assert 'value="Gasto"' in html
    assert 'value="150.00"' in html


def test_editar_gasto(client):
    _adicionar(client, "150", "2026-10-05")
    form = {"descricao": "Aluguel", "valor": "900", "categoria": "moradia", "data": "2026-10-06", "fixo": "on"}
    html = client.post("/editar/1", data=form, follow_redirects=True).get_data(as_text=True)
    assert "Gasto atualizado!" in html
    assert "Aluguel" in html
    assert 'class="selo-fixo"' in html


def test_editar_com_dados_invalidos_mantem_o_gasto(client):
    _adicionar(client, "150", "2026-10-05")
    form = {"descricao": "", "valor": "900", "categoria": "moradia", "data": "2026-10-06"}
    html = client.post("/editar/1", data=form, follow_redirects=True).get_data(as_text=True)
    assert "Preencha" in html
    assert 'value="150.00"' in html


def test_editar_gasto_inexistente_da_404(client):
    assert client.get("/editar/999").status_code == 404
    assert client.post("/editar/999", data={}).status_code == 404


def test_remover_pede_confirmacao(client):
    _adicionar(client, "150", "2026-10-05")
    html = client.get("/?mes=2026-10").get_data(as_text=True)
    assert "confirm(" in html


def test_previsao_some_nos_primeiros_dias_com_aviso(tmp_path):
    cliente = criar_cliente(tmp_path / "cedo.db", hoje=date(2026, 10, 3))
    cliente.post("/adicionar", data={"descricao": "Mercado", "valor": "300", "categoria": "alimentação", "data": "2026-10-02"})
    html = cliente.get("/?mes=2026-10").get_data(as_text=True)
    assert "Previsão para o fim do mês" not in html
    assert "poucos dados ainda" in html
