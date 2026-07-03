import csv

from collect_api import CODIGOS_TEMPO, montar_linha
from collect_scraping import para_celsius, para_hpa, para_kmh, primeiro_numero
from common import CAMPOS_CSV, salvar_csv


def test_primeiro_numero_com_virgula():
    assert primeiro_numero("18,3 °C") == 18.3


def test_para_celsius_converte_fahrenheit():
    assert para_celsius("64 °F") == 17.8


def test_para_celsius_mantem_celsius():
    assert para_celsius("18 °C") == 18.0


def test_para_kmh_converte_mph():
    assert para_kmh("10 mph") == 16.1


def test_para_hpa_converte_inhg():
    assert para_hpa("30.05 inHg") == 1017.6


def test_codigo_de_tempo_conhecido():
    atual = {"weather_code": 3, "temperature_2m": 20.0}
    linha = montar_linha(atual, "São Paulo", "Brasil")
    assert linha["condition"] == "Nublado"
    assert CODIGOS_TEMPO[0] == "Céu limpo"


def test_salvar_csv_grava_cabecalho_e_linha(tmp_path):
    saida = tmp_path / "clima.csv"
    linha = {campo: None for campo in CAMPOS_CSV}
    linha["city"] = "São Paulo"
    linha["source"] = "teste"

    salvar_csv(saida, linha)

    with saida.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        linhas = list(reader)

    assert reader.fieldnames == CAMPOS_CSV
    assert len(linhas) == 1
    assert linhas[0]["city"] == "São Paulo"
