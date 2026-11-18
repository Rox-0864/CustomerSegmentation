# Customer Segmentation

Análisis de segmentación de clientes sobre datos de ventas minoristas (Online Retail), con visualizaciones interactivas en Dash.

## Fuente de los datos

Dataset basado en *Online Retail* (UCI Machine Learning Repository): transacciones de un comercio minorista online del Reino Unido, con clientes ya anonimizados. Este proyecto lo usa con fines educativos. Las columnas fueron renombradas y las fechas desplazadas al período 2019-2020.

## Estructura

```
app/        Aplicación Dash (layout y callbacks)
pipeline/   Limpieza de datos y cálculo de RFM / segmentos
data/
  raw/        Dataset original (no versionado)
  processed/  Datos limpios y precalculados para la app
tests/      Tests del pipeline
```

## Puesta en marcha

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

Limpieza del dataset (genera `data/processed/clean_transactions.csv` y un log con las filas descartadas por paso):

```bash
python -m pipeline.clean --input Online_Retail.csv --output data/processed/clean_transactions.csv
```

Segmentación (genera `data/processed/rfm_segments.csv` y `segment_profile.csv`):

```bash
python -m pipeline.segment --input data/processed/clean_transactions.csv --k 4
# Métricas para elegir k:
python -m pipeline.segment --input data/processed/clean_transactions.csv --evaluate
```

Agregados del dashboard (genera `data/processed/monthly_revenue.csv`):

```bash
python -m pipeline.aggregate --input data/processed/clean_transactions.csv
```

Dashboard (http://127.0.0.1:8050):

```bash
python -m app.app
```

Tests:

```bash
pytest
```

## Despliegue

Dos versiones del mismo dashboard, con la misma lógica en `app/charts.py`:

- **Streamlit** (`streamlit_app.py`), para Streamlit Community Cloud.
- **Dash** (`app/app.py`), para hosting con Python (`gunicorn app.app:server`).

Ambas leen `data/public/`, que no contiene IDs de cliente y sí está versionado.

Publicar en Streamlit Community Cloud:

1. Subir el repositorio a GitHub.
2. En https://share.streamlit.io, crear una app con:
   - Repository y branch del proyecto.
   - Main file path: `streamlit_app.py`.
3. Cloud instala `requirements.txt` automáticamente.

Para regenerar los datos públicos después de cambiar el pipeline:

```bash
python -m pipeline.publish
```

Streamlit local:

```bash
streamlit run streamlit_app.py    # http://localhost:8501
```

## Estado

- [x] Estructura y dependencias (versiones fijadas)
- [x] Pipeline de limpieza con log de descartes (`data/processed/cleaning_log.json`)
- [x] RFM y segmentación (KMeans, k=4, nombres por perfil)
- [x] Visualizaciones en Dash y Streamlit (filtro por segmento, RFM, países, evolución mensual)
- [ ] Documentación técnica y funcional
