"""Coleta o clima atual pelo site timeanddate.com (scraping) e salva em CSV."""
import argparse
import re

import requests
from bs4 import BeautifulSoup

from common import agora, salvar_csv

URL_PADRAO = "https://www.timeanddate.com/weather/brazil/sao-paulo"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def baixar_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def primeiro_numero(texto):
    if not texto:
        return None
    m = re.search(r"-?\d+(?:[.,]\d+)?", texto)
    if not m:
        return None
    return float(m.group().replace(",", "."))


def para_celsius(texto):
    n = primeiro_numero(texto)
    if n is None:
        return None
    if texto and "°F" in texto:
        return round((n - 32) * 5 / 9, 1)
    return round(n, 1)


def para_kmh(texto):
    n = primeiro_numero(texto)
    if n is None:
        return None
    if texto and "mph" in texto.lower():
        return round(n * 1.60934, 1)
    return round(n, 1)


def para_hpa(texto):
    n = primeiro_numero(texto)
    if n is None:
        return None
    if texto and "hg" in texto.lower():  # polegadas de mercúrio
        return round(n * 33.8639, 1)
    return round(n, 1)


def extrair_fatos(texto_pagina):
    """Lê os detalhes da página (Humidity, Wind, Pressure...) e devolve um dict.

    O site mostra os itens no formato 'Rotulo: valor', então pego o valor de
    cada um até começar o próximo rótulo conhecido.
    """
    rotulos = ["Latest Report", "Visibility", "Pressure", "Humidity", "Dew Point", "Wind"]
    fatos = {}
    for i, rotulo in enumerate(rotulos):
        proximos = rotulos[i + 1:]
        parada = "|".join(re.escape(r) + ":" for r in proximos) or "$"
        m = re.search(rf"{re.escape(rotulo)}:\s*(.*?)(?={parada}|$)", texto_pagina, re.IGNORECASE)
        if m:
            fatos[rotulo] = m.group(1).strip(" |")
    return fatos


def coletar(url, cidade, pais):
    soup = BeautifulSoup(baixar_html(url), "html.parser")

    bloco = soup.select_one("#qlook")
    if bloco is None:
        raise RuntimeError("Não achei o bloco de clima atual (#qlook). O layout pode ter mudado.")

    texto = soup.get_text(" ", strip=True)
    fatos = extrair_fatos(texto)

    # temperatura fica em destaque no topo do bloco
    temp_el = bloco.select_one(".h2")
    temperatura = temp_el.get_text(" ", strip=True) if temp_el else None

    # a condição costuma ser o primeiro parágrafo do bloco
    condicao = None
    for p in bloco.select("p"):
        t = p.get_text(" ", strip=True)
        if t and not t.lower().startswith("feels like"):
            condicao = t.rstrip(".")
            break

    sensacao = None
    m = re.search(r"Feels Like:?\s*(-?\d+\s*°?\s*[CF])", texto, re.IGNORECASE)
    if m:
        sensacao = m.group(1)

    umidade = primeiro_numero(fatos.get("Humidity"))

    return {
        "source": "scraping_timeanddate",
        "city": cidade,
        "country": pais,
        "temperature_c": para_celsius(temperatura),
        "feels_like_c": para_celsius(sensacao),
        "condition": condicao,
        "humidity_percent": int(umidade) if umidade is not None else None,
        "wind_kmh": para_kmh(fatos.get("Wind")),
        "pressure_hpa": para_hpa(fatos.get("Pressure")),
        "reference_time": fatos.get("Latest Report"),
        "collected_at": agora(),
    }


def main():
    parser = argparse.ArgumentParser(description="Coleta clima atual por scraping (timeanddate).")
    parser.add_argument("--url", default=URL_PADRAO)
    parser.add_argument("--city", default="São Paulo")
    parser.add_argument("--country", default="Brasil")
    parser.add_argument("--output", default="data/weather_scraping.csv")
    args = parser.parse_args()

    try:
        linha = coletar(args.url, args.city, args.country)
    except (requests.RequestException, RuntimeError) as e:
        print(f"Erro ao coletar a página: {e}")
        raise SystemExit(1)

    salvar_csv(args.output, linha)
    print(f"CSV salvo em {args.output}")
    print(linha)


if __name__ == "__main__":
    main()
