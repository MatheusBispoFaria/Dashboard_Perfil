"""Recria os dados compactos do portfólio a partir do ZIP original do CP5."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
from zipfile import ZipFile


def prepare(source, output):
    spec = importlib.util.spec_from_file_location(
        "cp5_data_preparation", Path(__file__).with_name("cp5_data_preparation.py")
    )
    preparation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(preparation)
    names = [
        f"despesas_es_{year}_completo_parte_{part:02}.zip"
        for year in (2024, 2025) for part in range(1, 5)
    ]
    with tempfile.TemporaryDirectory() as directory, ZipFile(source) as archive:
        preparation.BASE_DIR = Path(directory)
        preparation.RAW_DIR = Path(directory)
        for name in names:
            with archive.open(f"cp5_datascience/data/raw/{name}") as input_file:
                with (Path(directory) / name).open("wb") as destination:
                    shutil.copyfileobj(input_file, destination)
        data = preparation.carregar_base()
        audit = preparation.auditoria_base()
        meta = preparation.metadata()

    output.mkdir(parents=True, exist_ok=True)
    data.to_csv(
        output / "despesas_es_2024_2025.csv.gz", index=False,
        date_format="%Y-%m-%d", float_format="%.17g",
        compression={"method": "gzip", "compresslevel": 6, "mtime": 0},
    )
    with source.open("rb") as archive_file:
        hasher = hashlib.sha256()
        for block in iter(lambda: archive_file.read(1024 * 1024), b""):
            hasher.update(block)
        digest = hasher.hexdigest()
    provenance = {
        "origem": "cp5_datascience.zip fornecido pelo autor do portfólio",
        "arquivo_sha256": digest, "arquivos": names,
        "areas": preparation.AREAS_MONITORADAS, "metadata": meta, "auditoria": audit,
        "tratamento": (
            "Tratamento original de src/data_service.py: reconstrução dos rótulos de 2025 "
            "pelos códigos oficiais de 2024, datas válidas e deduplicação por Id. "
            "Valores negativos preservados; nenhuma amostragem no recorte temático."
        ),
    }
    (output / "proveniencia.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Preparados {len(data):,} registros em {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Caminho do cp5_datascience.zip original")
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "despesas_es",
    )
    args = parser.parse_args()
    prepare(args.source, args.output)
