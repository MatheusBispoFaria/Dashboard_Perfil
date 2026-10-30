"""Verificações de comportamento para a organização modular do dashboard."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

from dashboard import create_app
from dashboard.config import PROJECT_ROOT
from dashboard.data import filter_dataset, load_dataset
from dashboard.statistics import proportion_interval


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
            "/assets/style.css", "/assets/profile.jpg",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                try:
                    self.assertEqual(response.status_code, 200)
                finally:
                    response.close()

    def test_navigation_and_each_section(self):
        sections = ("analise-dados", "quem-sou-eu", "qualificacoes", "skills")
        for section in sections:
            with self.subTest(section=section):
                selected = self.call_callback(
                    "active-section.data", [1, 1, 1, 1],
                    [f"nav-{section}.n_clicks"], ["analise-dados"],
                )
                self.assertEqual(selected["active-section"]["data"], section)
                for other in sections:
                    expected = "nav-item active" if other == section else "nav-item"
                    self.assertEqual(selected[f"nav-{other}"]["className"], expected)
                rendered = self.call_callback("tab-content-container.children", [section])
                self.assertIn("children", rendered["tab-content-container"])

    def test_sidebar_opens_and_closes(self):
        for before, after in (("sidebar", "sidebar collapsed"), ("sidebar collapsed", "sidebar")):
            response = self.call_callback("sidebar.className", [1], states=[before])
            self.assertEqual(response["sidebar"]["className"], after)

    def test_dashboard_updates_for_each_confidence_level(self):
        data = load_dataset()
        expected = data["renda_alta"].mean() * 100
        for confidence in ("off", "90", "95", "99"):
            with self.subTest(confidence=confidence):
                response = self.call_callback(
                    "graph-ocupacoes.figure", [None, None, None, None, None, confidence]
                )
                self.assertEqual(len(response), 9)
                gauge = response["graph-velocimetro"]["figure"]
                self.assertAlmostEqual(gauge["data"][0]["value"], expected)
                if confidence != "off":
                    self.assertIn(f"IC {confidence}%", gauge["layout"]["annotations"][0]["text"])

    def test_empty_selection_clears_figures(self):
        response = self.call_callback(
            "graph-ocupacoes.figure", [["inexistente"], None, None, None, None, "95"]
        )
        self.assertEqual(len(response), 9)
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
