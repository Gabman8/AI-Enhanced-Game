import numpy as np
import pandas as pd

# Configurar semilla para reproducibilidad
np.random.seed(42)

num_registros = 100000

print(f"Generando {num_registros} registros...")

# 1. Identificadores y tipo de enemigo
id_enemigo = np.random.randint(1, 1001, size=num_registros)
tipo_enemigo = np.random.choice(
    ["mago", "arquero", "cuerpo_a_cuerpo"],
    size=num_registros,
    p=[0.30, 0.30, 0.40],
)
nivel_enemigo = np.random.choice(
    range(1, 11),
    size=num_registros,
    p=[0.15, 0.15, 0.15, 0.12, 0.12, 0.10, 0.08, 0.06, 0.04, 0.03],
)

# 2. Atributos base del enemigo
vida_max_enemigo = round(100.0 + 10.0 * nivel_enemigo + np.random.uniform(-10, 10, num_registros), 2)
vida_actual_enemigo = round(np.random.uniform(0.0, 1.0, num_registros) * vida_max_enemigo, 2)
energia_enemigo = round(np.random.uniform(0.0, 100.0, num_registros), 2)

estado_enemigo = np.random.choice(
    ["reposo", "patrulla", "persecucion", "combate", "retirada", "explorando"],
    size=num_registros,
    p=[0.10, 0.30, 0.15, 0.25, 0.10, 0.10],
)

# 3. Posicionamiento y movimiento
pos_x_enemigo = round(np.random.uniform(0.0, 500.0, num_registros), 2)
pos_y_enemigo = round(np.random.uniform(0.0, 500.0, num_registros), 2)
dir_enemigo = np.random.choice(["N", "S", "E", "W"], size=num_registros)

# Velocidad sesgada hacia valores medios (Distribución Beta)
velocidad_enemigo = round(np.random.beta(a=3, b=3, size=num_registros) * 3.0, 2)

# Distancia al jugador condicionada por el estado de combate
distancia_jugador = np.where(
    estado_enemigo == "combate",
    np.random.beta(a=1, b=4, size=num_registros) * 15.0,  # Cerca si combate
    np.random.uniform(0.0, 100.0, num_registros),
)
distancia_jugador = round(distancia_jugador, 2)

# 4. Estado del Jugador
vida_jugador = round(np.clip(np.random.normal(70, 20, num_registros), 0, 100), 2)
velocidad_jugador = round(np.random.uniform(0.0, 5.0, num_registros), 2)
dir_jugador = np.random.choice(["N", "S", "E", "W"], size=num_registros)
jugador_corriendo = np.random.choice([0, 1], size=num_registros, p=[0.70, 0.30])
jugador_atacando = np.random.choice([0, 1], size=num_registros, p=[0.90, 0.10])

# El tipo de ataque depende de si está atacando
tipo_ataque_jugador = np.where(
    jugador_atacando == 1,
    np.random.choice(["cuerpo_a_cuerpo", "a_distancia", "magico"], size=num_registros, p=[0.50, 0.30, 0.20]),
    "ninguno",
)

danio_ultimo_recibido_jugador = round(np.random.uniform(0.0, 100.0, num_registros), 2)

# Combo del jugador con distribución sesgada hacia valores bajos
combo_jugador = np.random.geometric(p=0.15, size=num_registros) - 1
combo_jugador = np.clip(combo_jugador, 0, 50)

# Percepción del entorno
jugador_visible = np.random.choice([0, 1], size=num_registros, p=[0.50, 0.50])
ruido_jugador = round(np.random.beta(a=1, b=3, size=num_registros), 2)

# Amenaza (Heurística: Más alta si el jugador tiene mucha vida y está cerca)
amenaza_jugador = (vida_jugador / 100.0) * (1.0 - (distancia_jugador / 100.0))
amenaza_jugador = round(np.clip(amenaza_jugador, 0.0, 1.0), 2)

# 5. Entorno y Aliados
aliados_cerca = np.random.choice([0, 1, 2, 3, 4, 5], size=num_registros, p=[0.50, 0.30, 0.12, 0.05, 0.02, 0.01])
enemigos_cerca = np.random.choice([0, 1, 2, 3, 4, 5], size=num_registros, p=[0.50, 0.30, 0.12, 0.05, 0.02, 0.01])

cobertura_disponible = np.random.choice([0, 1], size=num_registros, p=[0.70, 0.30])
distancia_cobertura = np.where(
    cobertura_disponible == 1, round(np.random.uniform(0.0, 20.0, num_registros), 2), 0.0
)

botiquin_visible = np.random.choice([0, 1], size=num_registros, p=[0.90, 0.10])

# Tiempos e impactos históricos
tiempo_desde_ultimo_impacto = round(np.random.exponential(scale=5.0, size=num_registros), 2)
tiempo_desde_ultimo_impacto = np.clip(tiempo_desde_ultimo_impacto, 0.0, 30.0)

danio_ultimo_recibido_enemigo = round(np.random.uniform(0.0, 100.0, num_registros), 2)
asesinatos_enemigo = np.clip(np.random.geometric(p=0.2, size=num_registros) - 1, 0, 100)
asesinatos_jugador = np.clip(np.random.geometric(p=0.05, size=num_registros) - 1, 0, 100)

# Contexto de mapa
zona_mapa = np.random.choice(["bosque", "cueva", "mazmorra", "aldea"], size=num_registros)
terreno = np.random.choice(["grass", "stone", "road"], size=num_registros)
momento_dia = np.random.choice(["dia", "noche"], size=num_registros, p=[0.70, 0.30])
clima = np.random.choice(["despejado", "lluvia", "tormenta"], size=num_registros, p=[0.75, 0.20, 0.05])

# 6. CARACTERÍSTICAS DERIVADAS
porc_vida = round(vida_actual_enemigo / vida_max_enemigo, 4)
porc_energia = round(energia_enemigo / 100.0, 4)
delta_distancia = round(np.random.normal(0, 2.0, num_registros), 2)
delta_distancia = np.clip(delta_distancia, -10.0, 10.0)

en_desventaja = np.where(enemigos_cerca > aliados_cerca, 1, 0)

danio_recent_jugador = round(np.random.uniform(0.0, 100.0, num_registros), 2)
danio_recent_enemigo = round(np.random.uniform(0.0, 100.0, num_registros), 2)
linea_vista = jugador_visible

# Rango de ataque implícito basado en el tipo de enemigo
rango_ataque = np.select(
    [tipo_enemigo == "cuerpo_a_cuerpo", tipo_enemigo == "arquero", tipo_enemigo == "mago"],
    [3.0, 25.0, 20.0]
)
puede_atacar = np.where(distancia_jugador < rango_ataque, 1, 0)
puede_curar = np.where((porc_vida < 0.25) & (botiquin_visible == 1), 1, 0)

cooldown_restante = round(np.random.uniform(0.0, 10.0, num_registros), 2)
punt_agresion = round(np.random.uniform(0.0, 10.0, num_registros) / 10.0, 2)
punt_miedo = round(np.random.uniform(0.0, 10.0, num_registros) / 10.0, 2)

# 7. DETERMINACIÓN DE LA DECISIÓN (Simulación de árbol lógico para realismo)
decision = []
for i in range(num_registros):
    if puede_curar[i] == 1:
        decision.append("curar")
    elif en_desventaja[i] == 1 and porc_vida[i] < 0.3:
        decision.append(np.random.choice(["retirarse", "ocultarse"], p=[0.7, 0.3]))
    elif puede_atacar[i] == 1:
        if energia_enemigo[i] > 70 and punt_agresion[i] > 0.6:
            decision.append("ataque_fuerte")
        elif tipo_enemigo[i] in ["arquero", "mago"]:
            decision.append("ataque_distancia")
        else:
            decision.append(np.random.choice(["atacar", "bloquear", "esquivar"], p=[0.7, 0.15, 0.15]))
    elif estado_enemigo[i] == "combate" and puede_atacar[i] == 0:
        decision.append(np.random.choice(["perseguir", "flanquear"], p=[0.8, 0.2]))
    elif linea_vista[i] == 1 or ruido_jugador[i] > 0.6:
        decision.append("investigar")
    else:
        decision.append(np.random.choice(["patrulla", "esperar", "buscar", "vigilar"], p=[0.5, 0.2, 0.15, 0.15]))

# Construcción del DataFrame
df = pd.DataFrame({
    'id_enemigo': id_enemigo, 'tipo_enemigo': tipo_enemigo, 'nivel_enemigo': nivel_enemigo,
    'vida_actual_enemigo': vida_actual_enemigo, 'vida_max_enemigo': vida_max_enemigo,
    'energia_enemigo': energia_enemigo, 'estado_enemigo': estado_enemigo,
    'pos_x_enemigo': pos_x_enemigo, 'pos_y_enemigo': pos_y_enemigo, 'dir_enemigo': dir_enemigo,
    'velocidad_enemigo': velocidad_enemigo, 'distancia_jugador': distancia_jugador,
    'vida_jugador': vida_jugador, 'velocidad_jugador': velocidad_jugador, 'dir_jugador': dir_jugador,
    'jugador_corriendo': jugador_corriendo, 'jugador_atacando': jugador_atacando,
    'tipo_ataque_jugador': tipo_ataque_jugador, 'danio_ultimo_recibido_jugador': danio_ultimo_recibido_jugador,
    'combo_jugador': combo_jugador, 'jugador_visible': jugador_visible, 'ruido_jugador': ruido_jugador,
    'amenaza_jugador': amenaza_jugador, 'aliados_cerca': aliados_cerca, 'enemigos_cerca': enemigos_cerca,
    'cobertura_disponible': cobertura_disponible, 'distancia_cobertura': distancia_cobertura,
    'botiquin_visible': botiquin_visible, 'tiempo_desde_ultimo_impacto': tiempo_desde_ultimo_impacto,
    'danio_ultimo_recibido_enemigo': danio_ultimo_recibido_enemigo, 'asesinatos_enemigo': asesinatos_enemigo,
    'asesinatos_jugador': asesinatos_jugador, 'zona_mapa': zona_mapa, 'terreno': terreno,
    'momento_dia': momento_dia, 'clima': clima, 'porc_vida': porc_vida, 'porc_energia': porc_energia,
    'delta_distancia': delta_distancia, 'en_desventaja': en_desventaja, 'danio_reciente_jugador': danio_recent_jugador,
    'danio_reciente_enemigo': danio_recent_enemigo, 'linea_vista': linea_vista, 'puede_atacar': puede_atacar,
    'puede_curar': puede_curar, 'cooldown_restante': cooldown_restante, 'punt_agresion': punt_agresion,
    'punt_miedo': punt_miedo, 'decision': decision
})

# Guardar en archivo CSV
df.to_csv("dataset_enemigos_ml.csv", index=False)
print("¡Archivo 'dataset_enemigos_ml.csv' exportado exitosamente con 100k registros!")