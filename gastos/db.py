import sqlite3
from pathlib import Path

CAMINHO_PADRAO = Path("gastos.db")


def conectar(caminho=CAMINHO_PADRAO):
    """Abre a conexão com o banco. Use ':memory:' nos testes."""
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    criar_tabela(conexao)
    return conexao


def criar_tabela(conexao):
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL CHECK (valor > 0),
            categoria TEXT NOT NULL,
            data TEXT NOT NULL
        )
        """
    )
    conexao.commit()


def adicionar_gasto(conexao, descricao, valor, categoria, data):
    """Insere um gasto e devolve o id criado."""
    cursor = conexao.execute(
        "INSERT INTO gastos (descricao, valor, categoria, data) VALUES (?, ?, ?, ?)",
        (descricao, valor, categoria, data),
    )
    conexao.commit()
    return cursor.lastrowid


def listar_gastos(conexao, categoria=None, mes=None):
    """Devolve os gastos, do mais recente para o mais antigo.

    Filtros opcionais: categoria e mes (formato 'AAAA-MM').
    """
    sql = "SELECT * FROM gastos WHERE 1 = 1"
    parametros = []
    if categoria:
        sql += " AND categoria = ?"
        parametros.append(categoria)
    if mes:
        sql += " AND data LIKE ?"
        parametros.append(f"{mes}%")
    sql += " ORDER BY data DESC, id DESC"
    return conexao.execute(sql, parametros).fetchall()


def remover_gasto(conexao, gasto_id):
    """Remove um gasto. Devolve True se removeu, False se o id não existia."""
    cursor = conexao.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
    conexao.commit()
    return cursor.rowcount > 0


def total_por_categoria(conexao, mes=None):
    """Devolve uma lista de (categoria, total), do maior para o menor."""
    sql = "SELECT categoria, SUM(valor) AS total FROM gastos"
    parametros = []
    if mes:
        sql += " WHERE data LIKE ?"
        parametros.append(f"{mes}%")
    sql += " GROUP BY categoria ORDER BY total DESC"
    return conexao.execute(sql, parametros).fetchall()


def listar_categorias(conexao):
    linhas = conexao.execute("SELECT DISTINCT categoria FROM gastos ORDER BY categoria").fetchall()
    return [linha["categoria"] for linha in linhas]
