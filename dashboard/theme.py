"""Identidade visual compartilhada pelos gráficos."""

C_NAVY = "#262b2e"
C_BLUE = "#626bff"
C_LIGHT_BLUE = "#b4baff"
C_CYAN = "#69c9c7"

LAYOUT_CLEAN = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=12, r=12, t=14, b=20),
    font=dict(family="Inter, Segoe UI, sans-serif", size=10, color="#7d8595"),
    xaxis=dict(showgrid=False, gridcolor="#f0f1f7", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#f0f1f7", zeroline=False),
    hoverlabel=dict(bgcolor="#262b2e", bordercolor="#262b2e", font_color="#ffffff"),
)
