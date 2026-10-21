def mes_anterior(mes):
    """Recebe 'AAAA-MM' e devolve o mês anterior, também em 'AAAA-MM'."""
    ano, numero = (int(parte) for parte in mes.split("-"))
    if numero == 1:
        return f"{ano - 1}-12"
    return f"{ano}-{numero - 1:02d}"


def ultimos_meses(mes_final, quantidade):
    """Devolve uma lista com `quantidade` meses terminando em mes_final, do mais antigo ao mais novo."""
    meses = [mes_final]
    while len(meses) < quantidade:
        meses.insert(0, mes_anterior(meses[0]))
    return meses


NOMES_DOS_MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def mes_seguinte(mes):
    """Recebe 'AAAA-MM' e devolve o mês seguinte, também em 'AAAA-MM'."""
    ano, numero = (int(parte) for parte in mes.split("-"))
    if numero == 12:
        return f"{ano + 1}-01"
    return f"{ano}-{numero + 1:02d}"


def nome_do_mes(mes):
    """'2026-10' -> 'outubro de 2026'."""
    ano, numero = (int(parte) for parte in mes.split("-"))
    return f"{NOMES_DOS_MESES[numero - 1]} de {ano}"


def mes_valido(texto):
    """True se o texto está no formato 'AAAA-MM' com mês de 01 a 12."""
    if not texto or len(texto) != 7 or texto[4] != "-":
        return False
    ano, numero = texto[:4], texto[5:]
    return ano.isdigit() and numero.isdigit() and 1 <= int(numero) <= 12
