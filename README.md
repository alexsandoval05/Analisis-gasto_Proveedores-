# 📊 Kit de Análisis de Gasto y Proveedores (Excel + Power BI)

**Convierte las compras que exportas de tu ERP en un análisis Pareto de proveedores listo para tomar decisiones.**

Kit diseñado para **pymes** que quieren saber **en qué proveedores se concentra su gasto**, qué compras se hacen sin orden de compra y cuánto podrían ahorrar negociando precios, sin necesidad de un equipo de BI.

🛒 **Disponible en Hotmart:** [Kit de Análisis de Gasto y Proveedores](https://go.hotmart.com/L107878570E)

---

## 📑 Contenido

1. [Objetivo](#-objetivo)
2. [Descripción](#-descripción)
3. [Herramientas](#-herramientas)
4. [Flujo de trabajo: del ERP a Power BI](#-flujo-de-trabajo-del-erp-a-power-bi)
5. [Estructura de los datos](#-estructura-de-los-datos)
6. [Modelo y medidas DAX](#-modelo-y-medidas-dax)
7. [Dashboards](#-dashboards)
8. [Resultados (datos de ejemplo)](#-resultados-datos-de-ejemplo)
9. [Conclusiones](#-conclusiones)
10. [Estructura del kit](#-estructura-del-kit)
11. [Cómo usarlo](#-cómo-usarlo)

---

## 🎯 Objetivo

Identificar **qué proveedores concentran la mayor parte del gasto** de la empresa mediante un **análisis de Pareto (80/20) y clasificación ABC**, para:

- Enfocar la negociación en los pocos proveedores que mueven la mayor parte del dinero.
- Medir el **riesgo de dependencia** de proveedores (concentración Top 5 e índice HHI).
- Detectar **gasto sin orden de compra (OC)** por categoría.
- Cuantificar el **ahorro potencial** al comprar cada ítem al mejor precio ya pagado.

## 📝 Descripción

La mayoría de las pymes ya tiene toda la información en su ERP o software contable (facturas y órdenes de compra), pero no la analiza. Este kit propone un flujo sencillo:

1. **Exportar** las compras del ERP a Excel o CSV.
2. **Pegar** los datos en la plantilla de Excel con una estructura estándar.
3. **Actualizar** el archivo de Power BI, que calcula automáticamente todos los indicadores y muestra 3 dashboards interactivos, filtrables por **año, categoría y centro de costo**.

> ℹ️ Los datos que aparecen en las imágenes y resultados son **ficticios**, generados para demostrar el funcionamiento del kit (43 proveedores, 8 categorías, octubre 2024 – septiembre 2026).

## 🛠 Herramientas

| Herramienta | Uso |
|---|---|
| **Excel** | Plantilla estandarizada para recibir la exportación del ERP |
| **Power Query** | Limpieza, tipado de columnas y carga de datos (ETL) |
| **Power BI Desktop** | Modelo de datos, medidas DAX y dashboards |
| **DAX** | Pareto, clasificación ABC, HHI, plazo ponderado y ahorro potencial |

## 🔄 Flujo de trabajo: del ERP a Power BI

```
ERP / software contable  ──►  Exportación (Excel / CSV)  ──►  Plantilla Excel  ──►  Power Query  ──►  Modelo DAX  ──►  3 Dashboards
```

**¿Qué reporte exportar del ERP?** El reporte de **compras / facturas de proveedor detallado por ítem** (línea por línea), del período que quieras analizar. Casi todos los ERP usados en pymes (por ejemplo Siigo, Alegra, World Office, SAP Business One o Microsoft Dynamics) permiten exportarlo a Excel desde el módulo de **Compras** o **Cuentas por pagar**.

Recomendaciones antes de pegar los datos:
- Exporta **al menos 12 meses** para ver la tendencia y la estacionalidad.
- Usa **una fila por línea de factura** (no el total de la factura), para poder comparar precios por ítem.
- Unifica los nombres de proveedores (por ejemplo, "Andina Delta Ltda." y "ANDINA DELTA LTDA" deben quedar iguales); si el ERP trae el NIT, úsalo como clave.
- Asigna una **categoría** de gasto a cada línea (si el ERP no la trae, puedes mapearla desde la cuenta contable o el grupo de inventario).

## 🗂 Estructura de los datos

Cada fila de la plantilla corresponde a una línea de compra:

| Columna | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `Fecha` | Fecha | Fecha de la factura o compra | 2025-10-15 |
| `Proveedor` | Texto | Razón social del proveedor | Suministros Montaña Ltda. |
| `Categoria` | Texto | Categoría de gasto | Materias primas |
| `Centro_Costo` | Texto | Área o centro de costo que compra | Producción |
| `Item` | Texto | Producto o servicio con unidad | Ácido cítrico x kg |
| `Cantidad` | Número | Unidades compradas | 1.200 |
| `Precio_Unitario` | Número | Precio por unidad | 2,96 |
| `Monto` | Número | Cantidad × Precio unitario | 3.552,00 |
| `Numero_OC` | Texto | Número de orden de compra (vacío si no tiene) | OC-10452 |
| `Plazo_Pago_Dias` | Número | Días de plazo de pago acordados | 60 |

> ⚠️ Mantén los **nombres de columna exactamente iguales** a los de la plantilla; Power Query depende de ellos para actualizar el modelo.

**Categorías usadas en el ejemplo:** Materias primas, Logística, Servicios profesionales, Empaques, Mantenimiento (MRO), Marketing, TI y software, Servicios generales.

## 🧮 Modelo y medidas DAX

**Modelo:** tabla de hechos `Compras` con una tabla `Calendario` relacionada por `Fecha` (columnas `Año` y `AñoMes`).

### Indicadores generales

```DAX
Gasto Total = SUM ( Compras[Monto] )

N° Transacciones = COUNTROWS ( Compras )

N° Proveedores = DISTINCTCOUNT ( Compras[Proveedor] )

Gasto Sin OC =
CALCULATE ( [Gasto Total], ISBLANK ( Compras[Numero_OC] ) || Compras[Numero_OC] = "" )

% Gasto Sin OC = DIVIDE ( [Gasto Sin OC], [Gasto Total] )

Plazo Pago Ponderado =
DIVIDE ( SUMX ( Compras, Compras[Monto] * Compras[Plazo_Pago_Dias] ), [Gasto Total] )
```

### Pareto y clasificación ABC

```DAX
% Participación Proveedor =
DIVIDE ( [Gasto Total], CALCULATE ( [Gasto Total], ALLSELECTED ( Compras[Proveedor] ) ) )

% Acumulado Pareto =
VAR GastoActual = [Gasto Total]
VAR Tabla =
    ADDCOLUMNS ( ALLSELECTED ( Compras[Proveedor] ), "@Gasto", [Gasto Total] )
VAR Acumulado =
    SUMX ( FILTER ( Tabla, [@Gasto] >= GastoActual ), [@Gasto] )
RETURN
    DIVIDE ( Acumulado, CALCULATE ( [Gasto Total], ALLSELECTED ( Compras[Proveedor] ) ) )

Referencia 80% = 0.8

Clase ABC =
VAR Acum = [% Acumulado Pareto]
RETURN
    SWITCH ( TRUE (), Acum <= 0.80, "A", Acum <= 0.95, "B", "C" )

N° Proveedores 80% =
COUNTROWS (
    FILTER ( VALUES ( Compras[Proveedor] ), [% Acumulado Pareto] <= 0.80 )
)
```

### Riesgo de concentración

```DAX
Concentración Top 5 =
DIVIDE (
    SUMX ( TOPN ( 5, VALUES ( Compras[Proveedor] ), [Gasto Total] ), [Gasto Total] ),
    [Gasto Total]
)

-- Índice Herfindahl-Hirschman: suma de las participaciones al cuadrado (en puntos %)
Índice HHI =
SUMX ( VALUES ( Compras[Proveedor] ), ( [% Participación Proveedor] * 100 ) ^ 2 )

% Proveedor Principal =
DIVIDE ( MAXX ( VALUES ( Compras[Proveedor] ), [Gasto Total] ), [Gasto Total] )
```

**Cómo leer el HHI:** menos de 1.500 = gasto diversificado · 1.500 a 2.500 = concentración moderada · más de 2.500 = alta dependencia.

### Oportunidades de ahorro por ítem

```DAX
Precio Promedio = DIVIDE ( SUM ( Compras[Monto] ), SUM ( Compras[Cantidad] ) )

Precio Mínimo Proveedor =
MINX (
    VALUES ( Compras[Proveedor] ),
    DIVIDE ( CALCULATE ( SUM ( Compras[Monto] ) ), CALCULATE ( SUM ( Compras[Cantidad] ) ) )
)

Brecha Precio % = DIVIDE ( [Precio Promedio] - [Precio Mínimo Proveedor], [Precio Mínimo Proveedor] )

-- Lo que se habría ahorrado comprando todo el volumen al mejor precio pagado
Ahorro Potencial =
SUMX (
    VALUES ( Compras[Item] ),
    CALCULATE ( ( [Precio Promedio] - [Precio Mínimo Proveedor] ) * SUM ( Compras[Cantidad] ) )
)

% Ahorro Potencial = DIVIDE ( [Ahorro Potencial], [Gasto Total] )
```

> 💡 Las medidas pueden variar ligeramente frente al archivo `.pbix` del kit; el `.pbix` es la referencia final.

## 📈 Dashboards

### 1. Análisis de Gasto y Proveedores – Resumen
Vista general del gasto: KPIs principales (gasto total, N° de proveedores, % gasto sin OC, % ahorro potencial, índice HHI), evolución mensual del gasto y gasto por categoría.
**Filtros:** Año, Centro de costo, Categoría.

![Resumen](images/01_resumen.png)

### 2. Proveedores – Pareto
Gráfico de Pareto con la participación de cada proveedor, el % acumulado y la línea de referencia del 80%, junto con una tabla con la **clase ABC** de cada proveedor. KPIs: gasto total, N° de transacciones, N° de proveedores que suman el 80%, % gasto sin OC y plazo de pago ponderado.
**Filtros:** Año, Categoría.

![Pareto](images/02_pareto.png)

### 3. Riesgos y Oportunidades de Negocio
Concentración Top 5, índice HHI, gasto sin OC y ahorro potencial; % de gasto sin OC por categoría; dependencia del proveedor principal por categoría y tabla de **brecha de precios y ahorro potencial por ítem**.
**Filtros:** Año, Categoría.

![Riesgos y oportunidades](images/03_riesgos_oportunidades.png)

## 🔍 Resultados (datos de ejemplo)

| Indicador | Resultado |
|---|---|
| Gasto total analizado | **$9,55 millones** (≈2.000 transacciones, 43 proveedores) |
| Proveedores que concentran el 80% del gasto | **14 de 43** (33%) |
| Proveedor principal | Suministros Montaña Ltda. con **38,25%** del gasto |
| Concentración Top 5 | **58,72%** |
| Índice HHI | **≈1.650** → concentración moderada |
| Gasto sin orden de compra | **$678 mil (7,10%)**; el más alto en Servicios generales (13,89%) y Marketing (11,30%) |
| Ahorro potencial | **$562 mil (5,89% del gasto)** |
| Plazo de pago ponderado | **48,3 días** |
| Categoría con mayor gasto | Materias primas (≈$5 millones) |

## ✅ Conclusiones

- **Se cumple el principio de Pareto:** un tercio de los proveedores concentra el 80% del gasto. La negociación y el seguimiento deben enfocarse en los **14 proveedores clase A**.
- **Riesgo de dependencia:** un solo proveedor maneja más de un tercio del gasto, y en Materias primas el proveedor principal tiene el **72,71%** de la categoría. Conviene desarrollar proveedores alternativos.
- **Control de compras:** el gasto sin OC se concentra en servicios (generales, marketing, TI). Exigir OC en estas categorías mejora la trazabilidad y el control presupuestal.
- **Ahorro rápido:** comprar cada ítem al mejor precio ya pagado podría liberar cerca del **6% del gasto**. Los ítems con mayor ahorro (por ejemplo, ácido cítrico, hora de consultoría y fletes) son el punto de partida para negociar.

## 📁 Estructura del kit

```
Kit-Analisis-Gasto-Proveedores/
├── data/
│   └── Plantilla_Analisis_Gasto.xlsx        # Plantilla para pegar la exportación del ERP
├── powerbi/
│   └── Analisis_de_gasto_proveedores_V1.pbix # Modelo, medidas DAX y 3 dashboards
├── images/
│   ├── 01_resumen.png
│   ├── 02_pareto.png
│   └── 03_riesgos_oportunidades.png
└── README.md
```

## ▶️ Cómo usarlo

1. **Requisitos:** Microsoft Excel y [Power BI Desktop](https://powerbi.microsoft.com/desktop/) (gratuito, Windows).
2. **Exporta** desde tu ERP el reporte de compras detallado por ítem (Excel o CSV).
3. **Abre** `data/Plantilla_Analisis_Gasto.xlsx`, borra los datos de ejemplo y **pega tus datos** respetando el orden y el nombre de las columnas.
4. **Guarda** la plantilla en una carpeta fija de tu equipo.
5. **Abre** `powerbi/Analisis_de_gasto_proveedores_V1.pbix`.
6. Si cambiaste la ubicación del archivo: **Transformar datos → Configuración de origen de datos → Cambiar origen** y selecciona tu plantilla.
7. Haz clic en **Actualizar**. Los 3 dashboards se recalculan automáticamente.
8. Usa los filtros de **Año, Categoría y Centro de costo** para profundizar.

**Para actualizarlo cada mes:** pega las nuevas compras al final de la plantilla, guarda y presiona **Actualizar** en Power BI.

---

👤 **Autor:** Alexander Sandoval Moreno, Data Analyst | Ingeniero Químico, MBA | Lean Six Sigma Black Belt
[LinkedIn](http://www.linkedin.com/in/alexander-sandoval-m) · [GitHub](https://github.com/alexsandoval05/) · [Hotmart](https://go.hotmart.com/L107878570E)---
