# Controle de Gastos

Aplicação web em Flask para registrar e acompanhar gastos pessoais, com banco SQLite.

## Funcionalidades
- Cadastro de gastos (descrição, valor, categoria e data)
- Resumo do mês com total por categoria
- Filtro por mês e por categoria
- Remoção de gastos
- Exportação dos gastos para CSV (respeita o filtro de mês e categoria)
- Testes automatizados com pytest

## Como rodar
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Abra http://127.0.0.1:5000 no navegador.

## Testes
```bash
pytest
```

## Estrutura
```
app.py            # rotas Flask
gastos/db.py      # acesso ao banco (SQL)
templates/        # páginas HTML
static/           # CSS
tests/            # testes do banco e das rotas
```

## Tecnologias
Python, Flask, SQLite, HTML e CSS.
