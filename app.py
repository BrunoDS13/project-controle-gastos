import csv
import io
from datetime import date

from flask import Flask, Response, flash, redirect, render_template, request, url_for

from gastos import db

CATEGORIAS_SUGERIDAS = ["alimentação", "transporte", "moradia", "lazer", "saúde", "educação", "outros"]


def criar_app(caminho_banco=db.CAMINHO_PADRAO):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "troque-esta-chave-em-producao"
    app.config["CAMINHO_BANCO"] = caminho_banco

    def conexao():
        return db.conectar(app.config["CAMINHO_BANCO"])

    @app.route("/")
    def index():
        categoria = request.args.get("categoria") or None
        mes = request.args.get("mes") or date.today().strftime("%Y-%m")
        con = conexao()
        gastos = db.listar_gastos(con, categoria=categoria, mes=mes)
        totais = db.total_por_categoria(con, mes=mes)
        categorias = sorted(set(CATEGORIAS_SUGERIDAS) | set(db.listar_categorias(con)))
        con.close()

        total_geral = sum(t["total"] for t in totais)
        maior = max((t["total"] for t in totais), default=0)
        return render_template(
            "index.html",
            gastos=gastos,
            totais=totais,
            total_geral=total_geral,
            maior=maior,
            categorias=categorias,
            categoria_atual=categoria,
            mes=mes,
            hoje=date.today().isoformat(),
        )

    @app.route("/adicionar", methods=["POST"])
    def adicionar():
        descricao = request.form.get("descricao", "").strip()
        categoria = request.form.get("categoria", "").strip()
        data = request.form.get("data", "").strip()
        try:
            valor = float(request.form.get("valor", "").replace(",", "."))
            date.fromisoformat(data)
        except ValueError:
            valor = 0

        if not descricao or not categoria or valor <= 0:
            flash("Preencha descrição, categoria, data e um valor maior que zero.", "erro")
        else:
            con = conexao()
            db.adicionar_gasto(con, descricao, valor, categoria, data)
            con.close()
            flash("Gasto adicionado!", "ok")
        return redirect(url_for("index", mes=data[:7] if len(data) >= 7 else None))

    @app.route("/remover/<int:gasto_id>", methods=["POST"])
    def remover(gasto_id):
        con = conexao()
        removido = db.remover_gasto(con, gasto_id)
        con.close()
        flash("Gasto removido." if removido else "Gasto não encontrado.", "ok" if removido else "erro")
        return redirect(url_for("index", mes=request.form.get("mes") or None))

    @app.route("/exportar")
    def exportar():
        categoria = request.args.get("categoria") or None
        mes = request.args.get("mes") or None
        con = conexao()
        gastos = db.listar_gastos(con, categoria=categoria, mes=mes)
        con.close()

        saida = io.StringIO()
        escritor = csv.writer(saida)
        escritor.writerow(["data", "descricao", "categoria", "valor"])
        for g in gastos:
            escritor.writerow([g["data"], g["descricao"], g["categoria"], f"{g['valor']:.2f}"])

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
