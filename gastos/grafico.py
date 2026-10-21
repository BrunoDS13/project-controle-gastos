import io

from matplotlib.figure import Figure

from gastos.periodos import ultimos_meses

FUNDO = "#161b22"
TEXTO = "#e6edf3"
MUDO = "#8b949e"
DESTAQUE = "#3fb950"
APAGADO = "#2ea043"


def gerar_grafico_png(totais_por_mes, mes_final, quantidade=6):
    """Gera um gráfico de barras com os últimos meses e devolve os bytes do PNG.

    totais_por_mes: dicionário {'AAAA-MM': total}. Meses sem gastos aparecem com 0.
    """
    meses = ultimos_meses(mes_final, quantidade)
    valores = [totais_por_mes.get(mes, 0) for mes in meses]
    cores = [DESTAQUE if mes == mes_final else APAGADO for mes in meses]
    rotulos = [f"{mes[5:]}/{mes[:4]}" for mes in meses]

    figura = Figure(figsize=(7, 3.2), dpi=110, facecolor=FUNDO)
    eixo = figura.subplots()
    eixo.set_facecolor(FUNDO)

    barras = eixo.bar(rotulos, valores, color=cores, width=0.6)
    for barra, valor in zip(barras, valores):
        if valor > 0:
            eixo.text(
                barra.get_x() + barra.get_width() / 2,
                valor,
                f"R$ {valor:,.0f}".replace(",", "."),
                ha="center",
                va="bottom",
                color=TEXTO,
                fontsize=8,
            )

    eixo.set_title("Total gasto por mês", color=TEXTO, fontsize=11, loc="left")
    eixo.tick_params(colors=MUDO, labelsize=8)
    eixo.set_ylim(0, max(valores + [1]) * 1.18)
    eixo.yaxis.set_visible(False)
    for lado in ("top", "right", "left"):
        eixo.spines[lado].set_visible(False)
    eixo.spines["bottom"].set_color(MUDO)
    figura.tight_layout()

    buffer = io.BytesIO()
    figura.savefig(buffer, format="png", facecolor=FUNDO)
    return buffer.getvalue()
