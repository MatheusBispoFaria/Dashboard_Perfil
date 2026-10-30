"""Entrada para execução local e para publicação com Gunicorn."""

from dashboard import create_app

app = create_app()
server = app.server

if __name__ == "__main__":
    app.run(debug=True, port=8050)
