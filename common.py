import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TIMEZONE = "America/Sao_Paulo"

# Ordem das colunas do CSV. Os dois scripts (API e scraping) usam a mesma
# para dar pra comparar os arquivos depois.
CAMPOS_CSV = [
    "source",
    "city",
    "country",
    "temperature_c",
    "feels_like_c",
    "condition",
    "humidity_percent",
    "wind_kmh",
    "pressure_hpa",
    "reference_time",
    "collected_at",
]


def agora():
    """Horário atual de São Paulo em ISO (coluna collected_at)."""
    return datetime.now(ZoneInfo(TIMEZONE)).isoformat(timespec="seconds")


def salvar_csv(caminho, linha):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        writer.writeheader()
        writer.writerow(linha)
