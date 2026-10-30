"""Criação da aplicação e ligação entre telas, dados e callbacks."""

from dash import Dash
import dash_bootstrap_components as dbc

from .callbacks import register_callbacks
from .config import ASSETS_PATH, FONT_AWESOME_URL
from .data import load_dataset
from .layouts.analysis import create_analysis_layout
from .layouts.profile import (
    create_profile_layout,
    create_qualifications_layout,
    create_skills_layout,
)
from .layouts.shell import create_main_layout


def create_app():
    """Cria uma instância com dados e callbacks próprios."""
    data = load_dataset()
    app = Dash(
        __name__,
        assets_folder=str(ASSETS_PATH),
        external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME_URL],
        suppress_callback_exceptions=True,
    )
    sections = {
        "analise-dados": create_analysis_layout(data),
        "quem-sou-eu": create_profile_layout(),
        "qualificacoes": create_qualifications_layout(),
        "skills": create_skills_layout(),
    }
    app.layout = create_main_layout(app.get_asset_url("profile.jpg"))
    register_callbacks(app, data, sections)
    return app
