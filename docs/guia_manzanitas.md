# Guía del proceso, explicada con manzanitas 🍎

Imaginá que tenés un puesto de manzanas. Cada día anotás en un cuaderno cada venta: quién compró, cuántas manzanas y a qué precio. Después de un año, tenés un cuaderno enorme. Esta guía explica cómo pasamos de ese cuaderno a un panel que te dice qué clientes son tus mejores compradores.

Cada sección corresponde a una parte del proyecto.

---

## Paso 1: El cuaderno del puestero

Cada línea del cuaderno es una venta:

| Factura | Manzanas | Precio por manzana | Fecha | Cliente |
|---|---|---|---|---|
| 1001 | 6 | 2,55 | 1/12 | Ana |
| 1002 | 8 | 2,75 | 2/12 | Beto |
| 1003 | 6 | 3,39 | 3/12 | (sin nombre) |

Tenemos **541.909 líneas** como esta, de diciembre de 2019 a diciembre de 2020.

---

## Paso 2: Limpiar el cuaderno

Antes de contar, sacamos las anotaciones que no sirven:

- **Líneas repetidas**: alguien anotó dos veces la misma venta. Se borra una. *(5.268 líneas)*
- **Manzanas sin dueño**: no sabemos quién compró, así que no podemos saber cuál es su cliente. *(135.037 líneas)*
- **Devoluciones**: el cliente devolvió manzanas. Las anotamos con una "C" delante de la factura. No son ventas, así que se sacan. *(8.872 líneas)*
- **Anotaciones raras**: cantidad cero o negativa, o precio cero. Son errores o regalos. *(40 líneas)*

Quedan **392.692 líneas** de ventas válidas, de **4.338 clientes**. Cada paso queda registrado, para saber cuántas líneas se fueron en cada uno.

> **Dato curioso**: el cuaderno está escrito con letras de otra época (codificación latin-1). Si lo abrís con la configuración equivocada, el símbolo de libra (£) aparece roto. Por eso el programa lo lee de forma especial.

---

## Paso 3: Tres preguntas por cliente (RFM)

Para cada cliente, hacemos tres preguntas:

- **R: ¿Hace cuánto vino?** (Recencia). Un cliente que vino ayer tiene R = 1. Uno que no viene hace seis meses tiene R = 180.
- **F: ¿Cuántas veces vino?** (Frecuencia). Contamos las compras distintas, no las manzanas.
- **M: ¿Cuánto gastó en total?** (Monetario). Sumamos todo lo que pagó.

Ejemplo con dos clientes:

| Cliente | R (días) | F (compras) | M (gasto) |
|---|---|---|---|
| Ana | 3 | 15 | 900 |
| Beto | 200 | 1 | 40 |

Ana viene seguido, gasta mucho y vino hace poco. Beto vino una vez y hace mucho. Con solo mirar la tabla ya se ve que son clientes muy distintos.

---

## Paso 4: Poner todo en la misma balanza

Acá hay un problema. Un cliente puede gastar 280.000 y otro 40. Si los ponemos en la misma balanza tal cual, el de 280.000 aplasta a todos.

Lo arreglamos en dos pasos:

1. **Achicamos los números grandes** con una lupa especial (el logaritmo). Así 40 y 280.000 quedan más cerca. Es como medir distancias en metros en vez de milímetros.
2. **Ajustamos la balanza** para que R, F y M pesen lo mismo. Si no, los días (de 0 a 375) y el dinero (de 3 a 280.000) no se comparan.

---

## Paso 5: Hacer canastas de clientes parecidos (KMeans)

Ahora tenemos a cada cliente como un punto en un espacio de tres dimensiones. Queremos juntar en canastas a los que se parecen.

El algoritmo se llama **KMeans**. Le decimos cuántas canastas queremos (la **k**) y él:

1. Pone una piedra de color por canasta en un lugar al azar.
2. Cada cliente se mete en la canasta cuya piedra le quede más cerca.
3. Mueve cada piedra al centro de sus clientes.
4. Repite hasta que nadie cambie de canasta.

### ¿Cuántas canastas?

Probamos varias opciones y miramos dos cosas:

- **Qué tan apretadas quedan las canastas** (la inercia). Más canastas, siempre quedan más apretadas, pero llega un punto en que agregar más no ayuda mucho.
- **Qué tan bien separadas están** (el silhouette). Un número cercano a 1 significa canastas bien separadas.

Resultado: con **2 canastas** quedan muy separadas, pero es como decir "clientes buenos" y "clientes malos": demasiado general. Con **4 canastas** la separación sigue siendo razonable y cada canasta tiene una historia clara. Elegimos **4**.

---

## Paso 6: Ponerles nombre a las canastas

KMeans numera las canastas (0, 1, 2, 3), pero el número no significa nada. Les ponemos nombre mirando qué hay adentro:

- **Champions** 🍏🍏🍏: la canasta de las manzanas más caras y más frecuentes. Clientes que vienen seguido, hace poco, y gastan mucho. *(16,6 % de los clientes)*
- **Loyal** 🍏🍏: vienen con regularidad, gasto medio-alto. *(27 %)*
- **Potential** 🍏: vinieron recién, pero todavía compraron poco. Son la promesa. *(20,7 %)*
- **Dormant** 💤: hace mucho que no vienen y compraron poco. *(35,7 %)*

Un detalle importante: el programa le pone el nombre según el perfil de cada canasta, no según el número. Así, aunque KMeans cambie la numeración otro día, el nombre sigue siendo correcto.

---

## Paso 7: Contar las manzanas por mes

Sumamos las ventas de cada mes: cuánto se vendió, cuántas compras hubo y cuántos clientes vinieron. Lo guardamos en una tabla pequeña para que el panel la lea rápido, sin tener que releer el cuaderno entero cada vez.

Ojo: diciembre de 2020 está incompleto. El cuaderno termina el 9 de diciembre, así que ese mes parece caer, pero no es una caída real.

---

## Paso 8: La vitrina (el panel)

Ahora ponemos todo en una vitrina interactiva:

- **Filtro de canastas**: elegís qué segmentos querés ver. Los números de arriba (cuántos clientes, cuánto gastaron, cuánto gasta cada uno en promedio) se actualizan solos.
- **Puntos de clientes**: cada punto es una persona. Arriba a la izquierda están los mejores clientes; abajo a la derecha, los que se fueron.
- **Barras**: cuánta plata deja cada canasta.
- **Línea de meses**: cómo fueron las ventas mes a mes.

Esto se llama **interactivo** porque reacciona cuando tocás algo. En el código, cada vez que cambiás el filtro, una función (el *callback*) recibe tu elección y devuelve los gráficos nuevos.

---

## Paso 9: El control de calidad (los tests)

Antes de confiar en la balanza, la probamos con pesas conocidas. Eso son los tests:

- Si una línea tiene cantidad negativa, ¿se borra?
- Si un cliente compró dos veces el mismo día, ¿cuenta como dos compras o como una?
- Si el último día alguien compró a las 23:59, ¿su recencia da 1 o da 0? (Antes daba 0, un error que encontramos y corregimos.)

Hay 15 tests. Si alguno falla, algo cambió y hay que mirarlo antes de seguir.

---

## Paso 10: Repetir el proceso cuando llegan ventas nuevas

El cuaderno sigue creciendo. Cuando haya ventas nuevas, se repite el camino completo:

1. Limpiar el cuaderno.
2. Calcular las tres preguntas de cada cliente.
3. Armar las canastas.
4. Recalcular los agregados mensuales.
5. Abrir la vitrina.

Los clientes pueden cambiar de canasta con cada compra. Un Dormant que vuelve a comprar puede pasar a Potential o Loyal. Eso es bueno: significa que la estrategia funciona.

---

## Resumen en una sola frase

> Limpiamos el cuaderno de ventas, medimos a cada cliente con tres preguntas (cuándo vino, cuántas veces, cuánto gastó), juntamos en canastas a los que se parecen y mostramos el resultado en una vitrina para decidir a quién hablarle.

---

## Glosario de manzanitas

| Término técnico | En manzanitas |
|---|---|
| Dataset | El cuaderno de ventas |
| Limpieza | Sacar anotaciones repetidas, sin dueño o erróneas |
| RFM | Las tres preguntas por cliente: cuándo, cuántas veces, cuánto |
| Escalado | Poner todo en la misma balanza |
| Logaritmo | Una lupa que achica los números muy grandes |
| KMeans | Juntar en canastas a los que se parecen |
| k | Cuántas canastas queremos |
| Silhouette | Qué tan separadas quedan las canastas |
| Dashboard | La vitrina interactiva |
| Callback | Lo que pasa cuando tocás el filtro |
| Test | La prueba con pesas conocidas |
