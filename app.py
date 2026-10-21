import csv
import io
from datetime import date

from flask import Flask, Response, abort, flash, redirect, render_template, request, url_for

from gastos import db
from gastos.grafico import gerar_grafico_png
from gastos.periodos import mes_anterior
from gastos.previsao import prever_total

CATEGORIAS_SUGERIDAS = ["alimentação", "transporte", "moradia", "lazer", "saúde", "educação", "outros"]


def ler_formulario_gasto(form):
    """Lê e valida o formulário de gasto. Devolve (dados, erro); um dos dois é None."""
    descricao = form.get("descricao", "").strip()
    categoria = form.get("categoria", "").strip()
    data = form.get("data", "").strip()
    try:
        valor = float(form.get("valor", "").replace(",", "."))
        date.fromisoformat(data)
    except ValueError:
        valor = 0

    if not descricao or not categoria or valor <= 0:
        return None, "Preencha descrição, categoria, data e um valor maior que zero."
    dados = {"descricao": descricao, "valor": valor, "categoria": categoria, "data": data, "fixo": form.get("fixo") == "on"}
    return dados, None


def criar_app(caminho_banco=db.CAMINHO_PADRAO, hoje=date.today):
    """`hoje` devolve a data atual; os testes passam uma data fixa no lugar."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "troque-esta-chave-em-producao"
    app.config["CAMINHO_BANCO"] = caminho_banco

    def conexao():
        return db.conectar(app.config["CAMINHO_BANCO"])

    @app.route("/")
    def index():
        categoria = request.args.get("categoria") or None
        mes = request.args.get("mes") or hoje().strftime("%Y-%m")
        con = conexao()
        gastos = db.listar_gastos(con, categoria=categoria, mes=mes)
        totais = db.total_por_categoria(con, mes=mes)
        categorias = sorted(set(CATEGORIAS_SUGERIDAS) | set(db.listar_categorias(con)))
        mes_passado = mes_anterior(mes)
        total_passado = db.total_do_mes(con, mes_passado)
        total_fixo = db.total_fixo_do_mes(con, mes)
        meta = db.obter_meta(con, mes)
        con.close()

        total_geral = sum(t["total"] for t in totais)
        variacao = None
        if total_passado > 0:
            variacao = (total_geral - total_passado) / total_passado * 100
        maior = max((t["total"] for t in totais), default=0)

        previsao = prever_total(total_geral, mes, hoje(), total_fixo)

        progresso = None
        if meta:
            percentual = total_geral / meta * 100
            situacao = "ok" if percentual < 80 else "atencao" if percentual <= 100 else "estourou"
            progresso = {"percentual": percentual, "situacao": situacao, "restante": meta - total_geral}
            if previsao is not None:
                progresso["previsao_estoura"] = previsao > meta
                progresso["diferenca_previsao"] = abs(previsao - meta)
        return render_template(
            "index.html",
            gastos=gastos,
            totais=totais,
            total_geral=total_geral,
            mes_passado=mes_passado,
            total_passado=total_passado,
            variacao=variacao,
            meta=meta,
            previsao=previsao,
            progresso=progresso,
            maior=maior,
            categorias=categorias,
            categoria_atual=categoria,
            mes=mes,
            hoje=hoje().isoformat(),
        )

    @app.route("/adicionar", methods=["POST"])
    def adicionar():
        dados, erro = ler_formulario_gasto(request.form)
        if erro:
            flash(erro, "erro")
            return redirect(url_for("index", mes=request.form.get("data", "")[:7] or None))

        con = conexao()
        db.adicionar_gasto(con, **dados)
        con.close()
        flash("Gasto adicionado!", "ok")
        return redirect(url_for("index", mes=dados["data"][:7]))

    @app.route("/editar/<int:gasto_id>", methods=["GET", "POST"])
    def editar(gasto_id):
        con = conexao()
        gasto = db.buscar_gasto(con, gasto_id)
        if gasto is None:
            con.close()
            abort(404)

        if request.method == "POST":
            dados, erro = ler_formulario_gasto(request.form)
            if erro:
                con.close()
                flash(erro, "erro")
                return redirect(url_for("editar", gasto_id=gasto_id))
            db.atualizar_gasto(con, gasto_id, **dados)
            con.close()
            flash("Gasto atualizado!", "ok")
            return redirect(url_for("index", mes=dados["data"][:7]))

        categorias = sorted(set(CATEGORIAS_SUGERIDAS) | set(db.listar_categorias(con)))
        con.close()
        return render_template("editar.html", gasto=gasto, categorias=categorias)

    @app.route("/meta", methods=["POST"])
    def definir_meta():
        mes = request.form.get("mes", "").strip()
        try:
            valor = float(request.form.get("valor", "").replace(",", "."))
            date.fromisoformat(f"{mes}-01")
        except ValueError:
            valor = 0

        if valor <= 0:
            flash("Informe uma meta maior que zero.", "erro")
        else:
            con = conexao()
            db.definir_meta(con, mes, valor)
            con.close()
            flash("Meta atualizada!", "ok")
        return redirect(url_for("index", mes=mes or None))

    @app.route("/remover/<int:gasto_id>", methods=["POST"])
    def remover(gasto_id):
        con = conexao()
        removido = db.remover_gasto(con, gasto_id)
        con.close()
        flash("Gasto removido." if removido else "Gasto não encontrado.", "ok" if removido else "erro")
        return redirect(url_for("index", mes=request.form.get("mes") or None))

    @app.route("/grafico.png")
    def grafico():
        mes = request.args.get("mes") or hoje().strftime("%Y-%m")
        con = conexao()
        totais = db.total_por_mes(con)
        con.close()
        return Response(gerar_grafico_png(totais, mes), mimetype="image/png")

    @app.route("/exportar")
    def exportar():
        categoria = request.args.get("categoria") or None
        mes = request.args.get("mes") or None
        con = conexao()
        gastos = db.listar_gastos(con, categoria=categoria, mes=mes)
        con.close()

        saida = io.StringIO()
        escritor = csv.writer(saida)
        escritor.writerow(["data", "descricao", "categoria", "valor", "fixo"])
        for g in gastos:
            escritor.writerow([g["data"], g["descricao"], g["categoria"], f"{g['valor']:.2f}", "sim" if g["fixo"] else "nao"])

        nome = f"gastos-{mes}.csv" if mes else "gastos.csv"
        return Response(
            saida.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={nome}"},
        )

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(debug=True)
