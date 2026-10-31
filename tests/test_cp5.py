"""Integração do CP5 com os dados reais e os callbacks do portfólio."""

import json
import unittest

import test_dashboard

from dashboard import create_app
from dashboard.cp5.analytics import kpis, moeda
from dashboard.cp5.data import AREAS, filter_data, load_data, load_provenance
from dashboard.cp5.layout import GRAPHS


class CP5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.server.test_client()

    call_callback = test_dashboard.ApplicationTests.call_callback

    def test_prepared_data_matches_original_audit(self):
        data = load_data()
        audit = load_provenance()["auditoria"]
        self.assertEqual(len(data), audit["registros_recorte"])
        self.assertEqual(set(data["Funcao"]), set(AREAS))
        self.assertEqual(set(data["Ano"]), {2024, 2025})
        self.assertFalse(data["Id"].duplicated().any())
        for column, count in audit["valores_negativos_recorte"].items():
            self.assertEqual(int((data[column] < 0).sum()), count)
        self.assertNotIn("Favorecido", data.columns)
        self.assertNotIn("CpfCnpj", data.columns)

    def test_filters_update_indicators_and_all_eight_figures(self):
        filters = ["TRANSPORTE", [2025], "2025-01-01", "2025-06-30", None, None, None, None]
        response = self.call_callback("cp5-kpi-empenho.children", filters)
        selected = filter_data(*filters)
        self.assertGreater(len(selected), 0)
        self.assertLess(len(selected), len(load_data()))
        self.assertTrue(selected["Funcao"].eq("TRANSPORTE").all())
        self.assertTrue(selected["Ano"].eq(2025).all())
        totals = kpis(selected)
        for key in ("empenho", "liquidado", "pago", "rap"):
            self.assertEqual(response[f"cp5-kpi-{key}"]["children"], moeda(totals[key]))
        for key in GRAPHS:
            self.assertGreater(len(response[f"cp5-graph-{key}"]["figure"]["data"]), 0)
        expected = f"{len(selected):,} registros na seleção".replace(",", ".")
        self.assertEqual(response["cp5-record-count"]["children"], expected)

    def test_empty_filters_return_no_data_without_crashing(self):
        response = self.call_callback(
            "cp5-kpi-empenho.children",
            ["ALL", [2024, 2025], None, None, ["inexistente"], None, None, None],
        )
        self.assertEqual(response["cp5-kpi-pago"]["children"], "R$ 0,00")
        self.assertEqual(response["cp5-record-count"]["children"], "0 registros na seleção")
        for key in GRAPHS:
            self.assertEqual(response[f"cp5-graph-{key}"]["figure"]["data"], [])

    def test_records_are_paginated_and_sortable(self):
        filters = ["ALL", [2024, 2025], None, None, None, None, None, None]
        response = self.call_callback(
            "cp5-records.data", [*filters, 1, 15, [{"column_id": "ValorPago", "direction": "desc"}]],
            ["cp5-records.page_current"],
        )["cp5-records"]
        self.assertEqual(len(response["data"]), 15)
        self.assertEqual(response["page_current"], 1)
        self.assertGreater(response["page_count"], 1)
        values = [item["ValorPago"] for item in response["data"]]
        self.assertEqual(values, sorted(values, reverse=True))
        response = self.call_callback(
            "cp5-records.data", [*filters, 15000, 15, []], ["cp5-area.value"],
        )["cp5-records"]
        self.assertEqual(response["page_current"], 0)

    def test_changing_area_clears_dependent_filters(self):
        response = self.call_callback("cp5-locations.options", ["HABITAÇÃO", 0])
        for component in ("cp5-locations", "cp5-subfunctions", "cp5-programs", "cp5-units"):
            self.assertEqual(response[component]["value"], [])
            self.assertGreater(len(response[component]["options"]), 0)

    def test_all_cp5_analysis_buttons_open_the_empty_modal(self):
        for key, (title, _) in GRAPHS.items():
            with self.subTest(graph=key):
                clicked = json.dumps({"type": "open-analysis", "chart": f"cp5-{key}"}, sort_keys=True, separators=(",", ":"))
                response = self.call_callback("analysis-modal.is_open", [[1]], [f"{clicked}.n_clicks"])
                self.assertTrue(response["analysis-modal"]["is_open"])
                self.assertEqual(response["analysis-modal-title"]["children"], f"Análise de dados · {title}")


if __name__ == "__main__":
    unittest.main()
