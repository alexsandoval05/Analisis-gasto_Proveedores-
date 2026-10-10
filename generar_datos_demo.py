"""
Kit de Análisis de Gasto y Proveedores — Generador de datos demo
-----------------------------------------------------------------
Genera un dataset ficticio y realista de compras (24 meses) con:
  - Distribución Pareto del gasto (pocos proveedores concentran la mayoría)
  - Estacionalidad mensual y crecimiento leve
  - Compras sin orden de compra (gasto "maverick")
  - Variación de precio del mismo ítem entre proveedores (ahorro potencial)

Uso:
    python generar_datos_demo.py            # 2.000 filas, semilla 42
    python generar_datos_demo.py 5000 7     # 5.000 filas, semilla 7

Salida: datos_demo_gasto.csv (UTF-8, separador coma)
Todos los nombres de proveedores son ficticios.
"""

import sys
import numpy as np
import pandas as pd

N_FILAS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
SEMILLA = int(sys.argv[2]) if len(sys.argv) > 2 else 42
rng = np.random.default_rng(SEMILLA)

FECHA_INICIO = pd.Timestamp("2024-10-01")
FECHA_FIN = pd.Timestamp("2026-09-30")

# Categoría -> (peso en el gasto, subcategorías con ítems y precio unitario base)
CATALOGO = {
    "Materias primas": (0.38, {
        "Químicos": [("Ácido cítrico x kg", 2.8), ("Soda cáustica x kg", 1.1), ("Glicerina x kg", 1.9)],
        "Insumos base": [("Azúcar refinada x kg", 0.9), ("Almidón de maíz x kg", 1.2), ("Aceite vegetal x L", 1.6)],
    }),
    "Empaques": (0.18, {
        "Envases": [("Botella PET 500 ml", 0.12), ("Frasco vidrio 250 ml", 0.35)],
        "Embalaje": [("Caja corrugada 40x30", 0.65), ("Película stretch x rollo", 14.0), ("Etiqueta autoadhesiva x millar", 18.0)],
    }),
    "Logística": (0.14, {
        "Transporte nacional": [("Flete Bogotá-Medellín", 480.0), ("Flete Bogotá-Cali", 520.0), ("Flete Bogotá-Barranquilla", 760.0)],
        "Almacenamiento": [("Posición estiba x mes", 22.0)],
    }),
    "Mantenimiento (MRO)": (0.09, {
        "Repuestos": [("Rodamiento industrial", 38.0), ("Correa transportadora x m", 55.0), ("Sello mecánico", 120.0)],
        "Servicios técnicos": [("Mantenimiento preventivo línea", 650.0), ("Calibración de equipos", 180.0)],
    }),
    "Servicios profesionales": (0.07, {
        "Consultoría": [("Hora consultoría", 45.0)],
        "Auditoría y legal": [("Auditoría externa (fase)", 2400.0), ("Asesoría legal x mes", 900.0)],
    }),
    "TI y software": (0.06, {
        "Licencias": [("Licencia software x usuario/mes", 21.0), ("Suscripción nube x mes", 340.0)],
        "Hardware": [("Portátil corporativo", 780.0), ("Monitor 24 pulgadas", 140.0)],
    }),
    "Marketing": (0.05, {
        "Publicidad": [("Pauta digital (campaña)", 1500.0)],
        "Material POP": [("Exhibidor punto de venta", 95.0), ("Volantes x millar", 30.0)],
    }),
    "Servicios generales": (0.03, {
        "Aseo y cafetería": [("Servicio de aseo x mes", 850.0), ("Insumos cafetería (pedido)", 120.0)],
        "Seguridad": [("Vigilancia x mes", 1600.0)],
    }),
}

CENTROS_COSTO = ["Producción", "Calidad", "Logística", "Administración", "Comercial", "Mantenimiento"]
CC_POR_CATEGORIA = {
    "Materias primas": ["Producción"],
    "Empaques": ["Producción", "Logística"],
    "Logística": ["Logística", "Comercial"],
    "Mantenimiento (MRO)": ["Mantenimiento", "Producción"],
    "Servicios profesionales": ["Administración", "Calidad"],
    "TI y software": ["Administración", "Comercial", "Calidad"],
    "Marketing": ["Comercial"],
    "Servicios generales": ["Administración"],
}

PREFIJOS = ["Andina", "Comercial", "Distribuidora", "Grupo", "Industrias", "Suministros", "Inversiones", "Soluciones"]
NUCLEOS = ["del Valle", "Sabana", "Pacífico", "Altiplano", "Caribe", "Central", "Nova", "Prisma", "Atlas", "Delta",
           "Cóndor", "Ceiba", "Horizonte", "Montaña", "Río Claro", "Santa Fe", "Orión", "Aurora"]
SUFIJOS = ["S.A.S.", "S.A.", "Ltda."]


def nombres_proveedores(n):
    vistos, salida = set(), []
    while len(salida) < n:
        nombre = f"{rng.choice(PREFIJOS)} {rng.choice(NUCLEOS)} {rng.choice(SUFIJOS)}"
        if nombre not in vistos:
            vistos.add(nombre)
            salida.append(nombre)
    return salida


# 1) Proveedores por categoría, con peso tipo Pareto dentro de cada categoría
proveedores = {}
nombres = iter(nombres_proveedores(60))
contador = 1
for cat in CATALOGO:
    n_prov = rng.integers(4, 9)
    pesos = rng.pareto(1.2, n_prov) + 0.05
    pesos = pesos / pesos.sum()
    lista = []
    for p in pesos:
        # factor de precio: algunos proveedores cobran más por lo mismo
        lista.append({"id": f"PRV-{contador:03d}", "nombre": next(nombres),
                      "peso": p, "factor_precio": rng.uniform(0.92, 1.22),
                      "plazo": int(rng.choice([0, 15, 30, 45, 60, 90], p=[.08, .12, .35, .2, .17, .08]))})
        contador += 1
    proveedores[cat] = lista

# 2) Fechas con estacionalidad (picos en mar-abr y oct-nov) y crecimiento leve
dias = pd.date_range(FECHA_INICIO, FECHA_FIN, freq="D")
dias = dias[dias.dayofweek < 5]  # solo días hábiles
estacional = 1 + 0.25 * np.isin(dias.month, [3, 4, 10, 11]) - 0.15 * np.isin(dias.month, [1, 12])
tendencia = np.linspace(1.0, 1.15, len(dias))
p_dias = estacional * tendencia
p_dias = p_dias / p_dias.sum()

cats = list(CATALOGO)
p_cats = np.array([CATALOGO[c][0] for c in cats])

filas = []
for i in range(N_FILAS):
    fecha = dias[rng.choice(len(dias), p=p_dias)]
    cat = cats[rng.choice(len(cats), p=p_cats / p_cats.sum())]
    subcats = CATALOGO[cat][1]
    sub = rng.choice(list(subcats))
    item, precio_base = subcats[sub][rng.integers(len(subcats[sub]))]

    provs = proveedores[cat]
    prov = provs[rng.choice(len(provs), p=[p["peso"] for p in provs])]

    # Cantidad según orden de magnitud del precio
    if precio_base < 3:
        cantidad = int(rng.integers(500, 8000))
    elif precio_base < 50:
        cantidad = int(rng.integers(10, 400))
    elif precio_base < 500:
        cantidad = int(rng.integers(1, 25))
    else:
        cantidad = int(rng.integers(1, 4))

    inflacion = 1 + 0.0045 * ((fecha.year - 2024) * 12 + fecha.month - 10)  # ~5,5 % anual
    precio = round(precio_base * prov["factor_precio"] * inflacion * rng.normal(1, 0.03), 2)
    monto = round(cantidad * precio, 2)

    # Gasto maverick: más probable en compras pequeñas y servicios generales/marketing
    p_sin_oc = 0.06 + (0.12 if monto < 300 else 0) + (0.10 if cat in ("Servicios generales", "Marketing") else 0)
    tiene_oc = "No" if rng.random() < p_sin_oc else "Sí"

    filas.append({
        "ID_Transaccion": f"TX-{i + 1:05d}",
        "Fecha": fecha.date(),
        "ID_Proveedor": prov["id"],
        "Proveedor": prov["nombre"],
        "Categoria": cat,
        "Subcategoria": sub,
        "Item": item,
        "Centro_Costo": rng.choice(CC_POR_CATEGORIA[cat]),
        "Cantidad": cantidad,
        "Precio_Unitario": precio,
        "Monto": monto,
        "Moneda": "USD",
        "Orden_Compra": tiene_oc,
        "Plazo_Pago_Dias": prov["plazo"],
    })

df = pd.DataFrame(filas).sort_values(["Fecha", "ID_Transaccion"]).reset_index(drop=True)
df["ID_Transaccion"] = [f"TX-{i + 1:05d}" for i in range(len(df))]
df.to_csv("datos_demo_gasto.csv", index=False, encoding="utf-8")

# Resumen rápido para validar que el demo "cuenta una historia"
total = df["Monto"].sum()
top = df.groupby("Proveedor")["Monto"].sum().sort_values(ascending=False)
n80 = int((top.cumsum() / total <= 0.80).sum()) + 1
print(f"Filas: {len(df):,} | Gasto total: USD {total:,.0f}")
print(f"Proveedores: {top.size} | {n80} proveedores ({n80 / top.size:.0%}) concentran el 80 % del gasto")
print(f"Gasto sin orden de compra: {df.loc[df.Orden_Compra == 'No', 'Monto'].sum() / total:.1%}")
print(df.groupby("Categoria")["Monto"].sum().sort_values(ascending=False).map("{:,.0f}".format).to_string())
