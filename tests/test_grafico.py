from gastos.grafico import gerar_grafico_png

ASSINATURA_PNG = b"\x89PNG\r\n\x1a\n"


def test_gera_png_valido():
    png = gerar_grafico_png({"2026-10": 300.0, "2026-09": 200.0}, "2026-10")
    assert png.startswith(ASSINATURA_PNG)


def test_gera_png_sem_nenhum_gasto():
    png = gerar_grafico_png({}, "2026-10")
    assert png.startswith(ASSINATURA_PNG)
