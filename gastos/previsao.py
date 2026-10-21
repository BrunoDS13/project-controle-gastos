import calendar

# Antes disso há poucos dados e o ritmo gera números exagerados.
MIN_DIAS_PARA_PREVER = 7


def prever_total(total_ate_agora, mes, hoje, total_fixo=0):
    """Estima o total do mês com base no ritmo de gastos até hoje.

    Regra: gastos fixos (aluguel, assinaturas) não entram no cálculo do ritmo,
    porque acontecem uma vez só. Eles são somados como estão ao final.
        previsão = (gastos variáveis ÷ dia atual × dias do mês) + gastos fixos

    Só faz sentido para o mês em andamento: devolve None para meses passados,
    futuros, quando ainda não há gastos ou nos primeiros dias do mês
    (veja `poucos_dados`).
    mes: 'AAAA-MM'. hoje: objeto date.
    """
    if mes != hoje.strftime("%Y-%m") or total_ate_agora <= 0 or poucos_dados(mes, hoje):
        return None
    dias_no_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    variavel = total_ate_agora - total_fixo
    return variavel / hoje.day * dias_no_mes + total_fixo


def poucos_dados(mes, hoje):
    """True se o mês está em andamento mas ainda é cedo demais para uma previsão confiável."""
    return mes == hoje.strftime("%Y-%m") and hoje.day < MIN_DIAS_PARA_PREVER
