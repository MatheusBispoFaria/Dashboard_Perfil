"""Verificações de comportamento para a organização modular do dashboard."""

import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

from dashboard import create_app
from dashboard.config import DEFAULT_SECTION, NAV_ITEMS, PROJECT_ROOT
from dashboard.data import filter_dataset, load_dataset
from dashboard.statistics import proportion_interval
from dashboard.layouts.analysis import create_analysis_layout
from dashboard.layouts.cards import CARD_TITLES


class DataTests(unittest.TestCase):
    def test_loading_trims_text_and_preserves_optional_column_fallback(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as directory:
            path = Path(directory) / "sample.csv"
            pd.DataFrame({
                "income": [" >50K ", " <=50K "],
                "sex": [" Male ", " Female "],
                "occupation": [" Tech ", " Sales "],
                "age": [25, 40],
                "hours_per_week": [40, 35],
            }).to_csv(path, index=False)
            data = load_dataset(path)

        self.assertEqual(data["income"].tolist(), [">50K", "<=50K"])
        self.assertEqual(data["sex"].tolist(), ["Male", "Female"])
        self.assertEqual(data["occupation"].tolist(), ["Tech", "Sales"])
        self.assertEqual(data["renda_alta"].tolist(), [1, 0])
        self.assertEqual(data["workclass"].tolist(), ["N/A", "N/A"])
        self.assertEqual(data["education"].tolist(), ["N/A", "N/A"])

    def test_combined_filters_include_range_boundaries_without_changing_source(self):
        data = pd.DataFrame({
            "income": [">50K", ">50K", ">50K", "<=50K", ">50K", ">50K"],
            "workclass": ["Private", "Private", "Private", "Private", "Public", "Private"],
            "education": ["Bachelors", "Bachelors", "Bachelors", "Bachelors", "Bachelors", "Masters"],
            "age": [25, 40, 41, 30, 30, 30],
            "hours_per_week": [35, 45, 40, 40, 40, 40],
        })
        original = data.copy(deep=True)
        filtered = filter_dataset(
            data, [">50K"], ["Private"], ["Bachelors"], [25, 40], [35, 45]
        )
        self.assertEqual(filtered.index.tolist(), [0, 1])
        filtered.loc[0, "age"] = 99
        pd.testing.assert_frame_equal(data, original)

    def test_unselected_filters_keep_all_rows(self):
        data = load_dataset()
        pd.testing.assert_frame_equal(filter_dataset(data), data)

    def test_confidence_interval_and_empty_group(self):
        self.assertEqual(proportion_interval(0, 0, "95"), (0, 0))
        lower, upper = proportion_interval(50, 100, "95")
        self.assertAlmostEqual(lower, 40.2)
        self.assertAlmostEqual(upper, 59.8)
        lower_99, upper_99 = proportion_interval(50, 100, "99")
        self.assertLess(lower_99, lower)
        self.assertGreater(upper_99, upper)


class ApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.server.test_client()

    def call_callback(self, output_fragment, values, changed=(), states=None):
        key, callback = next(
            (key, callback)
            for key, callback in self.app.callback_map.items()
            if output_fragment in key
        )
        outputs = callback["output"]
        if isinstance(outputs, list):
            outputs = [
                {"id": output.component_id, "property": output.component_property}
                for output in outputs
            ]
        else:
            outputs = {"id": outputs.component_id, "property": outputs.component_property}
        response = self.client.post("/_dash-update-component", json={
            "output": key,
            "outputs": outputs,
            "inputs": [
                {**spec, "value": value}
                for spec, value in zip(callback["inputs"], values)
            ],
            "state": [
                {**spec, "value": value}
                for spec, value in zip(callback["state"], states or [])
            ],
            "changedPropIds": list(changed),
        })
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        return response.get_json()["response"]

    def test_server_and_assets(self):
        for path in (
            "/", "/_dash-layout", "/_dash-dependencies",
            "/assets/style.css", "/assets/profile.png", "/assets/chrome-ribbon.svg",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                try:
                    self.assertEqual(response.status_code, 200)
                finally:
                    response.close()

    def test_navigation_and_each_section(self):
        sections = [section for section, _, _ in NAV_ITEMS]
        for section in sections:
            with self.subTest(section=section):
                selected = self.call_callback(
                    "active-section.data", [1] * len(sections) + [0, "analise-dados"],
                    [f"nav-{section}.n_clicks"], ["analise-dados"],
                )
                self.assertEqual(selected["active-section"]["data"], section)
                for other in sections:
                    expected = "nav-item active" if other == section else "nav-item"
                    self.assertEqual(selected[f"nav-{other}"]["className"], expected)
                rendered = self.call_callback("tab-content-container.children", [section])
                self.assertIn("children", rendered["tab-content-container"])

    def test_top_navigation_opens_and_closes(self):
        for before, after, expanded in (
            ("top-navigation collapsed", "top-navigation", "true"),
            ("top-navigation", "top-navigation collapsed", "false"),
        ):
            response = self.call_callback("top-navigation.className", [1, 0], states=[before])
            self.assertEqual(response["top-navigation"]["className"], after)
            self.assertEqual(response["btn-toggle-navigation"]["aria-expanded"], expanded)

    def test_menu_starts_collapsed_and_modal_body_is_empty(self):
        def components(component):
            if isinstance(component, (list, tuple)):
                for child in component:
                    yield from components(child)
            elif hasattr(component, "to_plotly_json"):
                yield component
                yield from components(getattr(component, "children", None))

        by_id = {
            component.id: component for component in components(self.app.layout)
            if isinstance(getattr(component, "id", None), str)
        }
        self.assertIn("collapsed", by_id["top-navigation"].className)
        self.assertFalse(by_id["analysis-modal"].is_open)
        self.assertEqual(by_id["analysis-modal-body"].children, [])
        cards = list(components(create_analysis_layout(load_dataset())))
        arrows = [
            component.id["chart"] for component in cards
            if isinstance(getattr(component, "id", None), dict)
            and component.id.get("type") == "open-analysis"
        ]
        self.assertCountEqual(arrows, CARD_TITLES)

    def test_opening_stays_on_the_landing_page_until_navigation(self):
        response = self.call_callback(
            "active-section.data", [0] * len(NAV_ITEMS) + [0, "analise-dados"],
            states=[DEFAULT_SECTION],
        )
        self.assertEqual(response["active-section"]["data"], "inicio")
        self.assertTrue(all(response[f"nav-{section}"]["className"] == "nav-item" for section, _, _ in NAV_ITEMS))
        shell = self.call_callback("portfolio-shell.className", ["inicio"])
        self.assertIn("is-home", shell["portfolio-shell"]["className"])
        home = self.call_callback(
            "active-section.data", [0] * len(NAV_ITEMS) + [1, "cp5-data-science"],
            ["nav-inicio.n_clicks"], ["projetos"],
        )
        self.assertEqual(home["active-section"]["data"], "inicio")
        closed = self.call_callback(
            "top-navigation.className", [1, 1], ["nav-inicio.n_clicks"], ["top-navigation"],
        )
        self.assertEqual(closed["top-navigation"]["className"], "top-navigation collapsed")

    def test_analysis_switcher_keeps_one_main_navigation_and_remembers_choice(self):
        values = [0] * len(NAV_ITEMS) + [0, "cp5-data-science"]
        switched = self.call_callback(
            "active-section.data", values, ["analysis-selector.value"], ["analise-dados"],
        )
        self.assertEqual(switched["active-section"]["data"], "cp5-data-science")
        self.assertEqual(switched["nav-analise-dados"]["className"], "nav-item active")
        shell = self.call_callback("portfolio-shell.className", ["cp5-data-science"])
        self.assertIn("section-analysis", shell["portfolio-shell"]["className"])
        returned = self.call_callback(
            "active-section.data", values, ["nav-analise-dados.n_clicks"], ["projetos"],
        )
        self.assertEqual(returned["active-section"]["data"], "cp5-data-science")
        for section in ("inicio", "quem-sou-eu"):
            hidden = self.call_callback("active-section.data", values, ["analysis-selector.value"], [section])
            self.assertEqual(hidden["active-section"]["data"], section)
        rendered = self.call_callback("tab-content-container.children", ["cp5-data-science"])
        self.assertIn("Despesas públicas do Espírito Santo", json.dumps(rendered, ensure_ascii=False))

    def test_projects_start_collapsed_with_all_details_and_links_preserved(self):
        rendered = self.call_callback("tab-content-container.children", ["projetos"])
        def walk(node):
            if isinstance(node, list):
                for child in node:
                    yield from walk(child)
            elif isinstance(node, dict) and "props" in node:
                yield node
                yield from walk(node["props"].get("children"))
        components = list(walk(rendered["tab-content-container"]["children"]))
        projects = [node for node in components if node.get("type") == "Details" and "project-disclosure" in node["props"].get("className", "")]
        self.assertEqual(len(projects), 4)
        self.assertTrue(all(node["props"].get("open") is False for node in projects))
        self.assertTrue(all(node["props"]["children"][0]["type"] == "Summary" for node in projects))
        links = [node["props"]["href"] for node in components if node.get("type") == "A"]
        self.assertEqual(len(links), 5)
        self.assertIn("https://compiler-vzs3.onrender.com", links)
        text = json.dumps(rendered, ensure_ascii=False)
        self.assertIn("Chefon Ai · 5 integrantes", text)
        self.assertEqual(text.count("Novus Capital · 3 integrantes"), 2)
        self.assertNotIn("Ao lado de outros dois integrantes", text)
        self.assertIn("Minha experiência", text)

    def test_qualifications_remain_accessible_inside_about(self):
        rendered = self.call_callback("tab-content-container.children", ["quem-sou-eu"])
        content = json.dumps(rendered, ensure_ascii=False)
        self.assertIn("Formação e qualificações", content)
        self.assertIn("Certificações", content)
        self.assertIn("Chefon Ai · 5 integrantes", content)

    def test_each_arrow_opens_its_analysis_modal(self):
        for chart, title in CARD_TITLES.items():
            with self.subTest(chart=chart):
                clicked = json.dumps({"type": "open-analysis", "chart": chart}, sort_keys=True, separators=(",", ":"))
                clicks = [int(other == chart) for other in CARD_TITLES]
                response = self.call_callback(
                    "analysis-modal.is_open", [clicks], [f"{clicked}.n_clicks"]
                )
                self.assertTrue(response["analysis-modal"]["is_open"])
                self.assertEqual(response["analysis-modal-title"]["children"], f"Análise de dados · {title}")

    def test_reset_filters_restores_full_dataset_ranges(self):
        response = self.call_callback("filtro-renda.value", [1])
        data = load_dataset()
        for field in ("filtro-renda", "filtro-vinculo", "filtro-escolaridade"):
            self.assertEqual(response[field]["value"], [])
        self.assertEqual(response["filtro-ic"]["value"], "off")
        self.assertEqual(response["filtro-idade"]["value"], [int(data["age"].min()), int(data["age"].max())])
        self.assertEqual(response["filtro-jornada"]["value"], [int(data["hours_per_week"].min()), int(data["hours_per_week"].max())])

    def test_dashboard_updates_for_each_confidence_level(self):
        data = load_dataset()
        expected = data["renda_alta"].mean() * 100
        for confidence in ("off", "90", "95", "99"):
            with self.subTest(confidence=confidence):
                response = self.call_callback(
                    "graph-ocupacoes.figure", [None, None, None, None, None, confidence]
                )
                self.assertEqual(len(response), 10)
                self.assertEqual(response["selection-summary"]["children"], f"{len(data):,} registros na seleção".replace(",", "."))
                gauge = response["graph-velocimetro"]["figure"]
                self.assertAlmostEqual(gauge["data"][0]["value"], expected)
                if confidence != "off":
                    self.assertIn(f"IC {confidence}%", gauge["layout"]["annotations"][0]["text"])

    def test_empty_selection_clears_figures(self):
        response = self.call_callback(
            "graph-ocupacoes.figure", [["inexistente"], None, None, None, None, "95"]
        )
        self.assertEqual(len(response), 10)
        self.assertEqual(response["selection-summary"]["children"], "0 registros na seleção")
        for key, value in response.items():
            if key.startswith("graph-"):
                self.assertEqual(value["figure"]["data"], [])
        self.assertEqual(
            response["top-escolaridade-container"]["children"]["props"]["children"],
            "Sem dados para esta seleção.",
        )

    def test_entry_point_works_from_another_directory(self):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT)
        result = subprocess.run(
            [sys.executable, "-c", "from app import app, server; assert app.server is server; "
             "assert server.test_client().get('/assets/style.css').status_code == 200"],
            cwd=PROJECT_ROOT / "assets", env=environment, capture_output=True, text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
