import calendar


def prever_total(total_ate_agora, mes, hoje):
    """Estima o total do mês com base no ritmo de gastos até hoje.

    Só faz sentido para o mês em andamento: devolve None para meses passados,
    futuros ou quando ainda não há gastos.
    mes: 'AAAA-MM'. hoje: objeto date.
    """
    if mes != hoje.strftime("%Y-%m") or total_ate_agora <= 0:
        return None
    dias_no_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    return total_ate_agora / hoje.day * dias_no_mes
