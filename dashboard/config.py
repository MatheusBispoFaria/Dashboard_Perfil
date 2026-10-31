"""Caminhos e configurações compartilhadas da aplicação."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "adult_clean.csv"
ASSETS_PATH = PROJECT_ROOT / "assets"

FONT_AWESOME_URL = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
)

DEFAULT_SECTION = "inicio"
ANALYSIS_ITEMS = (
    ("analise-dados", "Renda e perfil socioeconômico"),
    ("cp5-data-science", "Despesas Públicas · ES"),
)
NAV_ITEMS = (
    ("analise-dados", "Análises de Dados", "fa-chart-line"),
    ("quem-sou-eu", "Quem Sou Eu", "fa-user"),
    ("skills", "Skills", "fa-lightbulb"),
    ("projetos", "Projetos", "fa-layer-group"),
)
