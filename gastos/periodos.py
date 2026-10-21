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
