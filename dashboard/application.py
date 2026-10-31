"""Criação da aplicação e ligação entre telas, dados e callbacks."""

from dash import Dash, html
import dash_bootstrap_components as dbc

from .callbacks import register_callbacks
from .config import ASSETS_PATH, FONT_AWESOME_URL
from .data import load_dataset
from .layouts.analysis import create_analysis_layout
from .layouts.profile import (
    create_about_layout,
    create_qualifications_layout,
    create_skills_layout,
)
from .layouts.shell import create_main_layout
from .layouts.projects import create_projects_layout
from .cp5.layout import create_cp5_layout
from .cp5.callbacks import register_cp5_callbacks


def create_app():
    """Cria uma instância com dados e callbacks próprios."""
    data = load_dataset()
    app = Dash(
        __name__,
        assets_folder=str(ASSETS_PATH),
        external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME_URL],
        suppress_callback_exceptions=True,
        title="Matheus | Portfólio Digital",
        update_title="Atualizando dados…",
    )
    sections = {
        "inicio": html.Div(),
        "analise-dados": create_analysis_layout(data),
        "quem-sou-eu": create_about_layout(),
        "qualificacoes": create_qualifications_layout(),
        "skills": create_skills_layout(),
        "projetos": create_projects_layout(),
        "cp5-data-science": create_cp5_layout,
    }
    app.layout = create_main_layout(
        app.get_asset_url("profile.png"), app.get_asset_url("chrome-ribbon.svg"),
    )
    register_callbacks(app, data, sections)
    register_cp5_callbacks(app)
    return app
