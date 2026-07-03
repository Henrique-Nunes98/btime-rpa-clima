"""Coleta o clima atual de São Paulo pela API do Open-Meteo e salva em CSV."""
import argparse

import requests

from common import agora, salvar_csv

URL = "https://api.open-meteo.com/v1/forecast"

# centro de São Paulo/SP
LAT_PADRAO = -23.5505
LON_PADRAO = -46.6333

# códigos de tempo da WMO usados pelo Open-Meteo
CODIGOS_TEMPO = {
    0: "Céu limpo",
    1: "Principalmente limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Neblina",
    48: "Neblina com gelo",
    51: "Garoa fraca",
    53: "Garoa moderada",
    55: "Garoa intensa",
    61: "Chuva fraca",
    63: "Chuva moderada",
    65: "Chuva forte",
    71: "Neve fraca",
    73: "Neve moderada",
    75: "Neve forte",
    80: "Pancadas de chuva fracas",
    81: "Pancadas de chuva moderadas",
    82: "Pancadas de chuva fortes",
    95: "Tempestade",
    96: "Tempestade com granizo",
    99: "Tempestade com granizo forte",
}


def buscar(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "weather_code,wind_speed_10m,pressure_msl"
        ),
        "timezone": "America/Sao_Paulo",
    }
    resp = requests.get(URL, params=params, timeout=20)
    resp.raise_for_status()

    atual = resp.json().get("current")
    if not atual:
        raise RuntimeError("A API não retornou o bloco 'current'.")
    return atual


def montar_linha(atual, cidade, pais):
    codigo = atual.get("weather_code")
    condicao = None
    if codigo is not None:
        condicao = CODIGOS_TEMPO.get(codigo, f"Código {codigo}")

    return {
        "source": "api_open_meteo",
        "city": cidade,
        "country": pais,
        "temperature_c": atual.get("temperature_2m"),
        "feels_like_c": atual.get("apparent_temperature"),
        "condition": condicao,
        "humidity_percent": atual.get("relative_humidity_2m"),
        "wind_kmh": atual.get("wind_speed_10m"),
        "pressure_hpa": atual.get("pressure_msl"),
        "reference_time": atual.get("time"),
        "collected_at": agora(),
    }


def main():
    parser = argparse.ArgumentParser(description="Coleta clima atual via API (Open-Meteo).")
    parser.add_argument("--latitude", type=float, default=LAT_PADRAO)
    parser.add_argument("--longitude", type=float, default=LON_PADRAO)
    parser.add_argument("--city", default="São Paulo")
    parser.add_argument("--country", default="Brasil")
    parser.add_argument("--output", default="data/weather_api.csv")
    args = parser.parse_args()

    try:
        atual = buscar(args.latitude, args.longitude)
    except (requests.RequestException, RuntimeError) as e:
        print(f"Erro ao consultar a API: {e}")
        raise SystemExit(1)

    linha = montar_linha(atual, args.city, args.country)
    salvar_csv(args.output, linha)

    print(f"CSV salvo em {args.output}")
    print(linha)


if __name__ == "__main__":
    main()
