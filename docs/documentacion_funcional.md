# Documentación funcional — Customer Segmentation

## 1. Objetivo

Agrupar a los clientes de una tienda minorista online según su comportamiento de compra, para que el equipo de marketing y de negocio pueda decidir a qué grupo dirigir cada acción: fidelizar, reactivar o captar.

Se presenta el resultado en un panel interactivo que cualquier persona del equipo puede consultar sin conocimientos técnicos.

## 2. Usuarios

- **Equipo de marketing**: decide campañas por segmento.
- **Equipo de negocio / dirección**: consulta KPIs de ingresos y tamaño de cada grupo.
- **Equipo de análisis de datos**: mantiene el pipeline y valida los resultados.

## 3. Datos de origen

Historial de ventas de un comercio minorista online, de diciembre de 2019 a diciembre de 2020 (datos hasta el 9 de diciembre de 2020).

| Dato | Valor |
|---|---|
| Filas originales | 541.909 |
| Filas utilizadas tras la limpieza | 392.692 |
| Clientes identificados | 4.338 |
| Ingresos brutos (transacciones válidas) | 8.887.209 |
| Participación de Reino Unido en ingresos | 82 % |

Limitaciones de los datos que el lector debe conocer:
- **Un 25 % de las filas no tiene cliente asociado.** No pueden segmentarse, por lo que quedan fuera del análisis.
- **Las cancelaciones se excluyen**, no se restan. Los ingresos mostrados son brutos.
- **El mercado está muy concentrado** en Reino Unido, por lo que el análisis geográfico tiene poco peso.
- **Diciembre de 2020 es parcial**, por lo que su caída en el gráfico mensual no es una caída real.

## 4. Reglas de negocio

### 4.1 Qué cuenta como venta válida

Se excluyen:
1. Registros duplicados.
2. Ventas sin cliente identificado.
3. Cancelaciones (facturas que empiezan con `C`).
4. Líneas con cantidad o precio cero o negativo.

### 4.2 Cómo se mide a un cliente

| Métrica | Pregunta que responde | Unidad |
|---|---|---|
| Recencia | ¿Hace cuánto compró por última vez? | días |
| Frecuencia | ¿Cuántas veces compró? | facturas |
| Monetario | ¿Cuánto gastó en total? | moneda del dataset |

La fecha de referencia para medir la recencia es el día siguiente a la última compra registrada en los datos.

### 4.3 Segmentos

| Segmento | Quién es | Acción sugerida |
|---|---|---|
| **Champions** (16,6 %) | Compran seguido, recientemente y gastan mucho | Fidelizar: programas VIP, acceso anticipado, no saturar |
| **Loyal** (27,0 %) | Compran con regularidad y gasto medio-alto | Mantener: recompensas por volumen, cross-selling |
| **Potential** (20,7 %) | Compraron recientemente, aún poco frecuentes | Crecer: incentivos para una segunda y tercera compra |
| **Dormant** (35,7 %) | Compraron una vez o pocas veces, hace mucho | Reactivar: campañas de reenganche, o aceptar que se fueron |

Los segmentos son una herramienta de decisión, no una verdad absoluta. Un cliente puede cambiar de segmento con cada nueva compra.

### 4.4 Cuántos segmentos

Se usan **cuatro segmentos**. Con dos, los grupos son demasiado generales para diseñar campañas distintas. Con cinco o más, los grupos se parecen entre sí y su diferencia no justifica acciones separadas. Esta elección debe validarla el equipo de negocio.

## 5. Funcionalidades del panel

**Filtro de segmentos.** Selector múltiple. Por defecto muestra los cuatro segmentos. Al cambiar la selección se actualizan los indicadores y los dos gráficos de segmentos.

**Indicadores (KPIs).**
- Clientes: cantidad de clientes del segmento o segmentos seleccionados.
- Gasto total: suma del gasto de esos clientes.
- Gasto promedio por cliente.

**Gráfico de dispersión RFM.** Cada punto es un cliente. El eje horizontal indica los días desde su última compra; el vertical, su gasto total en escala logarítmica. El color indica el segmento. Pasando el cursor se ve la frecuencia del cliente.

**Gráfico de barras por segmento.** Gasto total por segmento. La etiqueta de cada barra muestra la cantidad de clientes.

**Gráficos de clientes por país.** Cada cliente se asigna a su país de compra más frecuente. Son cuatro gráficos:
- **Clientes por país**: todos los países en barras verticales, sin desglose por segmento. Muestra el peso de Reino Unido frente al resto.
- **Reino Unido por segmento**: clientes británicos en cada segmento. Reino Unido tiene el 90 % de los clientes.
- **Otros países**: los 15 países con más clientes sin Reino Unido, apilados por segmento.
- **Top 15 con Reino Unido**: los 15 países con más clientes, incluido Reino Unido, apilados por segmento.

**Gráfico de ingresos mensuales.** Evolución del ingreso total mes a mes. Es el mismo para todos los filtros y no depende de la selección.

## 6. Cómo leer el panel

- Un punto **cerca del eje izquierdo y arriba** es un cliente reciente y de alto gasto: un Champion.
- Un punto **a la derecha y abajo** es un cliente que hace tiempo no compra y gastó poco: un Dormant.
- Una barra alta con pocos clientes indica un segmento de alto valor por cliente.
- Los ingresos mensuales suben hacia el último trimestre del dataset. Ese período incluye la temporada alta de fin de año.

## 7. Limitaciones del modelo

- El modelo no predice compras futuras; describe el comportamiento pasado.
- Los clusters se calculan sobre el dataset completo. Si entran datos nuevos, los segmentos pueden moverse.
- Los clientes con una sola compra se distribuyen así: 1.119 en Dormant, 350 en Potential y 24 en Loyal (estos últimos por su gasto). Ningún cliente con una sola compra es Champion.
- No se considera el tipo de producto ni el margen, solo el monto.

## 8. Privacidad

- Los clientes se identifican con un código numérico, no con nombre ni datos personales.
- El panel no muestra el código de cliente en ningún gráfico. Los datos son de un ejercicio con clientes ya anonimizados.

## 9. Próximos pasos

1. Validar con negocio los cuatro segmentos y sus acciones.
2. Revisar el panel en el navegador antes de publicarlo.
3. Incorporar ingresos netos (restando cancelaciones).
4. Definir cada cuánto se recalculan los datos cuando lleguen ventas nuevas.
