# Documentación técnica — Customer Segmentation

Este documento describe la arquitectura, el pipeline de datos, el modelo de segmentación, la aplicación web y la forma de ejecutar, probar y mantener el proyecto.

## 1. Stack y dependencias

| Componente | Versión | Uso |
|---|---|---|
| Python | 3.12 | Lenguaje principal |
| pandas | 3.1.1 | Limpieza y agregaciones |
| scikit-learn | 1.9.1 | KMeans, silhouette, escalado |
| Dash | 4.5.0 | Aplicación web interactiva |
| Streamlit | 1.67.0 | Aplicación web para Streamlit Community Cloud |
| Plotly | 7.1.0 | Gráficos interactivos (`plotly.express`) |
| pytest | 9.2.0 | Tests |

Las versiones están fijadas en `requirements.txt`.

## 2. Estructura del repositorio

```
app/
  charts.py              Gráficos, KPIs y carga de datos compartidos por ambas apps
  app.py                 Layout y callbacks de Dash
streamlit_app.py         Dashboard en Streamlit (en la raíz para Streamlit Cloud)
pipeline/
  clean.py               Limpieza del dataset crudo
  segment.py             RFM, escalado, KMeans y naming de segmentos
  aggregate.py           Agregados mensuales para el dashboard
data/
  raw/                   Dataset original (no versionado)
  processed/             Salidas del pipeline (ver sección 4), no versionadas
  public/                Datos sin IDs de cliente, que leen las apps y sí se versionan
tests/
  test_streamlit.py      Ejecución de la app Streamlit con AppTest
  test_clean.py          Reglas de limpieza
  test_segment.py        RFM y naming de segmentos
  test_app.py            KPIs, figuras y construcción de la app
docs/                    Documentación
pytest.ini               Configuración de pytest (pythonpath = raíz)
requirements.txt         Dependencias fijadas
```

## 3. Flujo de datos

```
Online_Retail.csv (raw, latin-1)
        │
        ▼  pipeline.clean
clean_transactions.csv ──────────────┬───────────────────────────┐
        │                            │                           │
        ▼  pipeline.segment          ▼  pipeline.aggregate       │
rfm_segments.csv                 monthly_revenue.csv             │
segment_profile.csv                  │                           │
        │                            │                           │
        └──────────────┬─────────────┘                           │
                       ▼                                         │
                 app/app.py (Dash)  ◄────────────────────────────┘
                                     (solo para trazabilidad; la app no lo lee)
```

La aplicación lee únicamente `rfm_segments.csv` y `monthly_revenue.csv`. No procesa las transacciones en cada carga, lo que mantiene el consumo de recursos bajo.

## 4. Pipeline

### 4.1 Limpieza (`pipeline/clean.py`)

Entrada: `Online_Retail.csv`, codificado en **latin-1** (contiene `£` como byte `0xA3`; leerlo como UTF-8 falla).

Reglas, en orden. Cada paso registra las filas descartadas en `data/processed/cleaning_log.json`:

| Paso | Regla | Filas descartadas |
|---|---|---|
| 1 | Duplicados exactos | 5.268 |
| 2 | `CUSTOMER_ID` vacío | 135.037 |
| 3 | Factura que empieza con `C` (cancelación) | 8.872 |
| 4 | `QUANTITY ≤ 0` o `UNIT_PRICE ≤ 0` | 40 |
| 5 | `INVOICE_DATE` no parseable | 0 |

Resultado: **541.909 → 392.692 filas**, 4.338 clientes.

Transformaciones:
- `INVOICE_DATE` se parsea con formato `%d/%m/%Y %H:%M`.
- `TOTAL_PRICE = QUANTITY × UNIT_PRICE`.
- `REGION` se renombra a `COUNTRY`. El nombre original es engañoso: contiene países.

Limitación conocida: las cancelaciones se excluyen y no se restan, por lo que los ingresos son **brutos de transacciones válidas**, no ingresos netos de devoluciones.

### 4.2 RFM y segmentación (`pipeline/segment.py`)

**Features por cliente:**
- `recency`: días entre la última compra y la fecha de referencia. La referencia es la fecha máxima del dataset normalizada a medianoche, más 1 día. Así una compra del último día tiene recencia 1.
- `frequency`: número de facturas distintas (`INVOICE_NO.nunique()`).
- `monetary`: suma de `TOTAL_PRICE`.
- `country`: país más frecuente del cliente. Solo 8 de 4.338 clientes compraron desde más de un país.

**Preparación:**
1. `log1p` sobre las tres variables, porque la distribución es muy asimétrica (mediana de gasto 669 frente a máximo de 280.206).
2. `StandardScaler` para que ninguna variable domine la distancia.

**Modelo:** `KMeans(n_clusters=k, n_init=10, random_state=42)`. La semilla fija asegura reproducibilidad.

**Elección de k:**

| k | Inercia | Silhouette |
|---|---|---|
| 2 | 6.477 | 0,433 |
| 3 | 4.858 | 0,336 |
| **4** | **3.926** | **0,333** |
| 5 | 3.269 | 0,318 |
| 6 | 2.842 | 0,313 |

k=2 maximiza el silhouette, pero produce dos grupos demasiado gruesos para acciones de marketing. k=3 y k=4 son casi equivalentes en silhouette; se eligió **k=4** por interpretabilidad. La decisión es de negocio y debe validarse con el equipo.

**Naming:** los ids de cluster de KMeans son arbitrarios y pueden cambiar entre corridas. Los nombres se asignan por perfil:
- Mayor `monetary` → **Champions**
- Mayor `recency` → **Dormant**
- De los dos restantes, mayor `frequency` → **Loyal**; el otro → **Potential**

**Perfil resultante (k=4, 4.338 clientes):**

| Segmento | Clientes | % | Recencia (mediana, días) | Frecuencia (mediana) | Gasto (mediana) |
|---|---|---|---|---|---|
| Champions | 718 | 16,6 % | 9 | 10 | 3.688 |
| Loyal | 1.172 | 27,0 % | 52 | 4 | 1.358 |
| Potential | 900 | 20,7 % | 20 | 2 | 415 |
| Dormant | 1.548 | 35,7 % | 187 | 1 | 303 |

### 4.3 Agregados (`pipeline/aggregate.py`)

`monthly_revenue.csv` contiene, por mes: `revenue`, `orders` (facturas distintas) y `customers` (clientes distintos). Diciembre de 2020 está incompleto (datos hasta el 9 de diciembre).

## 5. Aplicación web (`app/app.py`)

- Framework: Dash. Expone `server` (Flask) para despliegue con gunicorn.
- `load_data()` lee los dos CSV precalculados.
- Funciones puras para construir figuras y KPIs (`rfm_scatter`, `segment_bars`, `monthly_line`, `kpis`), testeables sin levantar el servidor.
- `build_app()` define el layout y el callback.

**Callback:** `Input("segment-filter", "value")` → `Output` de tres KPIs y de los gráficos `rfm-scatter`, `segment-bars` y `country-bars`. El gráfico mensual es estático.

**Gráficos por país** (cuatro, complementarios):
- `country_totals`: barras verticales con los clientes de todos los países, sin desglose por segmento.
- `uk_by_segment`: clientes de Reino Unido por segmento. Reino Unido concentra el 90 % de los clientes.
- `other_countries`: los 15 países con más clientes sin Reino Unido, apilados por segmento.
- `country_bars`: los 15 países con más clientes, incluido Reino Unido, apilados por segmento.

**Privacidad:** el gráfico RFM no incluye `CUSTOMER_ID` ni en el tooltip ni en `customdata`, así que el identificador no viaja al navegador. `CUSTOMER_ID` solo se usa del lado del servidor para agregar datos. El archivo `rfm_segments.csv` sí contiene los IDs y está excluido del repositorio (`.gitignore`). Los datos son de un ejercicio con clientes ya anonimizados.

## 6. Ejecución

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m pipeline.clean --input Online_Retail.csv --output data/processed/clean_transactions.csv
python -m pipeline.segment --input data/processed/clean_transactions.csv --k 4
python -m pipeline.aggregate --input data/processed/clean_transactions.csv

python -m app.app          # http://127.0.0.1:8050
pytest                     # 15 tests
```

Para desplegar en producción: `gunicorn app.app:server`, con `debug=False`.

## 7. Pruebas

| Archivo | Cubre |
|---|---|
| `test_clean.py` | Cada regla de limpieza, con un caso válido y uno inválido |
| `test_segment.py` | Valores de RFM para un cliente conocido; regresión de recencia 0; naming por perfil |
| `test_app.py` | KPIs (incluido selección vacía), orden de segmentos, trazas, construcción de la app, carga de datos reales |

## 8. Mantenimiento

- **Datos nuevos**: volver a ejecutar los tres comandos del pipeline. Los nombres de segmentos se recalculan solos.
- **Cambio de k**: revisar `--evaluate` y el perfil antes de cambiarlo. Los nombres dependen de k=4.
- **Dependencias**: actualizar `requirements.txt` solo tras correr `pytest`.
- **Tests**: ejecutar `pytest` antes de cada commit.

## 9. Pendientes

- Inicializar el repositorio Git y publicarlo en GitHub.
- Validar k=4 con el equipo de negocio.
- Ingresos netos (restando cancelaciones) como métrica alternativa.
