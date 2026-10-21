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


def test_exportar_csv_compativel_com_excel(client):
    form = {"descricao": "Mercado", "valor": "150,50", "categoria": "alimentação", "data": "2026-10-05"}
    client.post("/adicionar", data=form)
    resposta = client.get("/exportar?mes=2026-10")
    assert resposta.mimetype == "text/csv"
    assert "attachment" in resposta.headers["Content-Disposition"]
    assert "gastos-2026-10.csv" in resposta.headers["Content-Disposition"]
    assert resposta.data.startswith(b"\xef\xbb\xbf")  # BOM UTF-8
    linhas = resposta.data.decode("utf-8-sig").splitlines()
    assert linhas[0] == "data;descrição;categoria;valor;fixo"
    assert linhas[1] == "2026-10-05;Mercado;alimentação;150,50;não"


def test_exportar_csv_de_todos_os_meses(client):
    _adicionar(client, "100", "2026-09-10")
    _adicionar(client, "200", "2026-10-10")
    resposta = client.get("/exportar")
    assert "gastos-todos-os-meses.csv" in resposta.headers["Content-Disposition"]
    assert len(resposta.data.decode("utf-8-sig").splitlines()) == 3  # cabeçalho + 2 gastos


def test_exportar_com_mes_invalido_da_400(client):
    assert client.get("/exportar?mes=lixo").status_code == 400


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


def test_chave_secreta_vem_da_variavel_de_ambiente(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "minha-chave-de-teste")
    assert criar_app(tmp_path / "a.db").config["SECRET_KEY"] == "minha-chave-de-teste"


def test_sem_variavel_a_chave_e_aleatoria_e_nao_fixa(tmp_path, monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    chave_a = criar_app(tmp_path / "a.db").config["SECRET_KEY"]
    chave_b = criar_app(tmp_path / "b.db").config["SECRET_KEY"]
    assert chave_a != chave_b
    assert len(chave_a) >= 32


def test_navegacao_entre_meses(client):
    html = client.get("/?mes=2026-01").get_data(as_text=True)
    assert "janeiro de 2026" in html
    assert "mes=2025-12" in html and "dezembro de 2025" in html
    assert "mes=2026-02" in html and "fevereiro de 2026" in html


def test_mes_invalido_cai_no_mes_atual(client):
    for ruim in ["abc", "2026-13", "", "2026-1"]:
        resposta = client.get(f"/?mes={ruim}")
        assert resposta.status_code == 200
        assert "outubro de 2026" in resposta.get_data(as_text=True)
    assert client.get("/grafico.png?mes=lixo").status_code == 200


def test_historico_lista_todos_os_meses(client):
    _adicionar(client, "100", "2026-08-10")
    _adicionar(client, "150", "2026-09-10")
    _adicionar(client, "300", "2026-10-10")
    html = client.get("/historico").get_data(as_text=True)
    assert "agosto de 2026" in html and "setembro de 2026" in html and "outubro de 2026" in html
    assert "R$ 300.00" in html
    assert "R$ 183.33" in html  # média de 100, 150 e 300
    assert "100.0%" in html  # outubro dobrou em relação a setembro
    assert "mes=2026-09" in html  # link para abrir o mês


def test_historico_mostra_situacao_da_meta(client):
    _adicionar(client, "900", "2026-10-10")
    client.post("/meta", data={"mes": "2026-10", "valor": "1000"})
    html = client.get("/historico").get_data(as_text=True)
    assert "R$ 1000.00" in html
    assert "90%" in html
    assert "situacao-atencao" in html


def test_historico_sem_nenhum_gasto_mostra_so_o_mes_atual(client):
    resposta = client.get("/historico")
    assert resposta.status_code == 200
    assert "outubro de 2026" in resposta.get_data(as_text=True)
