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
    colunas = [linha["name"] for linha in conexao.execute("PRAGMA table_info(gastos)")]
    if "fixo" not in colunas:
        # bancos criados antes dessa coluna recebem o campo sem perder dados
        conexao.execute("ALTER TABLE gastos ADD COLUMN fixo INTEGER NOT NULL DEFAULT 0")
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS metas (
            mes TEXT PRIMARY KEY,
            valor REAL NOT NULL CHECK (valor > 0)
        )
        """
    )
    conexao.commit()


def adicionar_gasto(conexao, descricao, valor, categoria, data, fixo=False):
    """Insere um gasto e devolve o id criado. `fixo` marca gastos recorrentes (aluguel, assinaturas)."""
    cursor = conexao.execute(
        "INSERT INTO gastos (descricao, valor, categoria, data, fixo) VALUES (?, ?, ?, ?, ?)",
        (descricao, valor, categoria, data, int(fixo)),
    )
    conexao.commit()
    return cursor.lastrowid


def buscar_gasto(conexao, gasto_id):
    """Devolve um gasto pelo id, ou None se não existir."""
    return conexao.execute("SELECT * FROM gastos WHERE id = ?", (gasto_id,)).fetchone()


def atualizar_gasto(conexao, gasto_id, descricao, valor, categoria, data, fixo=False):
    """Atualiza todos os campos de um gasto. Devolve True se o id existia."""
    cursor = conexao.execute(
        "UPDATE gastos SET descricao = ?, valor = ?, categoria = ?, data = ?, fixo = ? WHERE id = ?",
        (descricao, valor, categoria, data, int(fixo), gasto_id),
    )
    conexao.commit()
    return cursor.rowcount > 0


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


def total_do_mes(conexao, mes):
    """Soma todos os gastos de um mês ('AAAA-MM'). Devolve 0 se não houver nenhum."""
    linha = conexao.execute(
        "SELECT COALESCE(SUM(valor), 0) AS total FROM gastos WHERE data LIKE ?",
        (f"{mes}%",),
    ).fetchone()
    return linha["total"]


def total_por_mes(conexao):
    """Devolve um dicionário {'AAAA-MM': total} com todos os meses que têm gastos."""
    linhas = conexao.execute(
        "SELECT substr(data, 1, 7) AS mes, SUM(valor) AS total FROM gastos GROUP BY mes"
    ).fetchall()
    return {linha["mes"]: linha["total"] for linha in linhas}


def definir_meta(conexao, mes, valor):
    """Define (ou troca) a meta de gastos a partir de um mês ('AAAA-MM')."""
    conexao.execute(
        "INSERT INTO metas (mes, valor) VALUES (?, ?) "
        "ON CONFLICT(mes) DO UPDATE SET valor = excluded.valor",
        (mes, valor),
    )
    conexao.commit()


def obter_meta(conexao, mes):
    """Devolve a meta em vigor no mês: a mais recente definida até ele, ou None."""
    linha = conexao.execute(
        "SELECT valor FROM metas WHERE mes <= ? ORDER BY mes DESC LIMIT 1", (mes,)
    ).fetchone()
    return linha["valor"] if linha else None


def total_fixo_do_mes(conexao, mes):
    """Soma só os gastos marcados como fixos em um mês ('AAAA-MM')."""
    linha = conexao.execute(
        "SELECT COALESCE(SUM(valor), 0) AS total FROM gastos WHERE fixo = 1 AND data LIKE ?",
        (f"{mes}%",),
    ).fetchone()
    return linha["total"]
