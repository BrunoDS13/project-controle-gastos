import calendar


def prever_total(total_ate_agora, mes, hoje, total_fixo=0):
    """Estima o total do mês com base no ritmo de gastos até hoje.

    Regra: gastos fixos (aluguel, assinaturas) não entram no cálculo do ritmo,
    porque acontecem uma vez só. Eles são somados como estão ao final.
        previsão = (gastos variáveis ÷ dia atual × dias do mês) + gastos fixos

    Só faz sentido para o mês em andamento: devolve None para meses passados,
    futuros ou quando ainda não há gastos.
    mes: 'AAAA-MM'. hoje: objeto date.
    """
    if mes != hoje.strftime("%Y-%m") or total_ate_agora <= 0:
        return None
    dias_no_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    variavel = total_ate_agora - total_fixo
    return variavel / hoje.day * dias_no_mes + total_fixo
