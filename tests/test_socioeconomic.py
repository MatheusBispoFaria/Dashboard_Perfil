"""Valida recortes, denominadores, pequenos grupos e rastreabilidade da consulta."""

import io
import json
import unittest

import pandas as pd

import test_dashboard
from dashboard import create_app
from dashboard.charts import create_dashboard_figures, create_hours_age_figure
from dashboard.data import apply_iqr, calculate_iqr_bounds, load_dataset, select_dataset
from dashboard.interpretations import analysis_body
from dashboard.labels import OCCUPATION
from dashboard.socioeconomic import hours_summary, occupation_summary, query_records


class SocioeconomicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_dataset()
        cls.app = create_app()
        cls.client = cls.app.server.test_client()

    call_callback = test_dashboard.ApplicationTests.call_callback

    def filters(self, sex=None, outliers=None):
        return [[], [], [], [17,90], [1,99], sex or [], outliers or [], "off"]

    def test_iqr_limits_are_fixed_and_constant_columns_are_kept(self):
        bounds = calculate_iqr_bounds(self.data)
        self.assertEqual(bounds, {"age": (-2.0,78.0), "hours_per_week": (32.5,52.5)})
        selected, removed, before = select_dataset(self.data, outliers=["iqr"])
        self.assertEqual((len(selected),removed,before),(23499,9062,32561))
        self.assertTrue(selected["age"].le(78).all())
        self.assertTrue(selected["hours_per_week"].between(32.5,52.5).all())
        female = self.data[self.data.sex.eq("Female")]
        filtered,_,_=select_dataset(self.data, sex=["Female"], outliers=["iqr"])
        pd.testing.assert_frame_equal(filtered, apply_iqr(female,bounds))
        constant=pd.DataFrame({"age":[30]*3,"hours_per_week":[40]*3})
        pd.testing.assert_frame_equal(apply_iqr(constant,calculate_iqr_bounds(constant)),constant)

    def test_sex_and_income_filter_preserve_the_original_data(self):
        original=self.data.copy(deep=True)
        selected,_,_=select_dataset(self.data,income=[">50K"],sex=["Female"])
        self.assertTrue(selected.sex.eq("Female").all())
        self.assertTrue(selected.income.eq(">50K").all())
        self.assertEqual(len(selected),1179)
        pd.testing.assert_frame_equal(self.data,original)

    def test_stacked_counts_and_gender_denominators_match_the_rows(self):
        figures=create_dashboard_figures(self.data)
        for chart in ("graph-genero","graph-escolaridade"):
            actual=sum(sum(trace.y if chart=="graph-genero" else trace.x) for trace in figures[chart].data)
            self.assertEqual(actual,len(self.data))
        gender=figures["graph-genero"]
        male=gender.data[1].customdata[0]
        self.assertEqual(male[0],21790)
        self.assertAlmostEqual(male[1],6662/21790*100)
        self.assertAlmostEqual(male[2],21790/32561*100)
        self.assertEqual(set(figures),{"graph-renda","graph-genero","graph-escolaridade","graph-ocupacoes","graph-idade-renda","graph-horas-idade"})

    def test_age_area_includes_zero_for_unobserved_age_and_legend(self):
        figure=create_dashboard_figures(self.data)["graph-idade-renda"]
        self.assertEqual(list(figure.data[0].x),list(range(17,91)))
        for trace in figure.data:
            self.assertEqual(trace.y[list(trace.x).index(89)],0)
            self.assertEqual(trace.stackgroup,"income")
            self.assertIn("US$",trace.name)

    def test_hours_points_expose_real_sample_sizes_and_no_interval_for_one_row(self):
        figure=create_hours_age_figure(self.data,"95")
        for age, expected in ((86,40),(87,2)):
            groups=hours_summary(self.data)
            group=groups[groups.age.eq(age)].iloc[0]
            self.assertEqual(group["count"],1)
            trace=next(t for t in figure.data if ("Acima" in t.name)==(group.income==">50K"))
            index=list(trace.x).index(age)
            self.assertEqual(trace.y[index],expected)
            self.assertEqual(trace.customdata[index][0],1)
            self.assertEqual(trace.marker.symbol[index],"circle-open")
            self.assertTrue(pd.isna(trace.error_y.array[index]))

    def test_occupation_ranking_keeps_missing_out_and_means_use_individual_rows(self):
        summary=occupation_summary(self.data)
        self.assertEqual(summary.occupation.head(3).tolist(),["Prof-specialty","Craft-repair","Exec-managerial"])
        for row in summary.head(3).itertuples():
            group=self.data[self.data.occupation.eq(row.occupation)]
            self.assertEqual(row.count,len(group))
            self.assertAlmostEqual(row.mean_age,group.age.mean())
            self.assertIn(row.occupation,OCCUPATION)

    def test_initial_iqr_and_gender_filters_reach_every_graph(self):
        response=self.call_callback("graph-ocupacoes.figure",self.filters(sex=["Female"],outliers=["iqr"]))
        selected,removed,before=select_dataset(self.data,sex=["Female"],outliers=["iqr"])
        pie=response["graph-renda"]["figure"]["data"][0]
        self.assertEqual(sum(pie["values"]),len(selected))
        gender=response["graph-genero"]["figure"]["data"]
        self.assertTrue(all(t["x"]==["Feminino"] for t in gender))
        self.assertIn(f"{removed:,}".replace(",","."),response["socio-filter-note"]["children"])
        self.assertEqual(response["socio-selection"]["data"]["sex"],["Female"])

    def test_table_pagination_search_sort_and_reset_are_consistent(self):
        values=[*self.filters(),"Feminino",1,15,[{"column_id":"age","direction":"desc"}]]
        response=self.call_callback("socio-records.data",values,["socio-records.page_current"])
        table=response["socio-records"]
        self.assertEqual(table["page_current"],1)
        self.assertEqual(len(table["data"]),15)
        self.assertTrue(all(r["sex"]=="Feminino" for r in table["data"]))
        ages=[r["age"] for r in table["data"]]
        self.assertEqual(ages,sorted(ages,reverse=True))
        reset=self.call_callback("socio-records.data",values,["filtro-genero.value"])
        self.assertEqual(reset["socio-records"]["page_current"],0)
        # Pontuação é texto literal, não expressão regular.
        self.assertTrue(query_records(self.data,"[inexistente]").empty)

    def test_csv_contains_the_whole_search_and_not_just_the_visible_page(self):
        states=[*self.filters(),"Feminino",[]]
        result=self.call_callback("socio-download.data",[1],["socio-export.n_clicks"],states)
        download=result["socio-download"]["data"]
        exported=pd.read_csv(io.StringIO(download["content"].lstrip("\ufeff")),sep=";")
        self.assertEqual(len(exported),10771)
        self.assertTrue(exported["Gênero (sexo na fonte)"].eq("Feminino").all())
        self.assertFalse(download["base64"])

    def test_modal_uses_the_current_snapshot_and_keeps_full_base_separate(self):
        chart="graph-genero"
        clicked=json.dumps({"type":"open-analysis","chart":chart},sort_keys=True,separators=(",",":"))
        result=self.call_callback("analysis-modal.is_open",[[1]],[f"{clicked}.n_clicks"],
                                  [{"sex":["Female"],"outliers":[],"confidence":"95"}])
        text=json.dumps(result["analysis-modal-body"],ensure_ascii=False)
        self.assertIn("10.771",text)
        self.assertIn("Referência sem filtros",text)
        self.assertIn("32.561",text)
        self.assertNotIn("nan%",text)


if __name__=="__main__":
    unittest.main()
