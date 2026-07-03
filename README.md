# Teste Btime - Dev RPA | Coleta de Clima

Desafio de RPA: coletar o clima atual de São Paulo de duas formas e salvar em CSV.

- `collect_scraping.py` — pega os dados direto do site (timeanddate.com).
- `collect_api.py` — pega os dados da API pública do Open-Meteo.

Os dois geram um CSV com as mesmas colunas, então dá pra comparar os resultados.

## Fontes

- Scraping: https://www.timeanddate.com/weather/brazil/sao-paulo
- API: https://api.open-meteo.com/v1/forecast (sem chave de autenticação)

## Estrutura

```
btime-rpa-clima/
├── collect_scraping.py   # coleta pelo site
├── collect_api.py        # coleta pela API
├── common.py             # colunas do CSV + função pra salvar
├── data/                 # CSVs gerados ao rodar os scripts (não versionados)
├── tests/
├── requirements.txt
└── README.md
```

## Colunas do CSV

`source`, `city`, `country`, `temperature_c`, `feels_like_c`, `condition`,
`humidity_percent`, `wind_kmh`, `pressure_hpa`, `reference_time`, `collected_at`.

O scraping vem em unidades variadas (°F, mph, inHg), então converto tudo para
Celsius, km/h e hPa antes de salvar, pra bater com o formato da API.

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Coleta pela API:

```bash
python collect_api.py
```

Coleta por scraping:

```bash
python collect_scraping.py
```

Dá pra trocar cidade/saída pelos parâmetros. Ex.:

```bash
python collect_api.py --latitude -22.9068 --longitude -43.1729 \
  --city "Rio de Janeiro" --output data/weather_api_rj.csv

python collect_scraping.py \
  --url "https://www.timeanddate.com/weather/brazil/rio-de-janeiro" \
  --city "Rio de Janeiro" --output data/weather_scraping_rj.csv
```

## Testes

```bash
pytest
```

## Observações

- Os CSVs são gravados em `data/` ao rodar os scripts e são sobrescritos a cada execução (a pasta fica versionada, os arquivos não).
- Se o site bloquear o acesso ou mudar o layout, o scraping avisa o erro e
  encerra sem quebrar. A parte de parsing fica no `collect_scraping.py`, então
  é lá que se ajusta se o HTML mudar.
