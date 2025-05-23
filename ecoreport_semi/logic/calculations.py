# Creado por Alejandro Venegas Robles.
# En caso de incidencias, contactar con alejandro2196vr@gmail.com
# -*- coding: utf-8 -*-
"""
Funciones para cálculos derivados basados en los datos del informe.
Ej: Clasificación FEVI, estimación de presiones de llenado VI, score VExUS.
"""
from models import InformeEcoCompleto, MedidasVI, MedidasAuriculas, PresionesLlenadoVI, VExUSScore
import config
from utils.error_handling import log_message

def calcular_clasificacion_fevi(medidas_vi: MedidasVI, medidas_ai: MedidasAuriculas) -> str:
    # --- INICIO: Marcador para localización de errores (Cálculo FEVI) ---
    try:
        if medidas_vi.fevi_porcentaje is None:
            return "No valorada"
        
        fevi = medidas_vi.fevi_porcentaje
        ai_vol = medidas_ai.ai_vol_ml_m2

        if fevi <= config.FEVI_REDUCIDA_MAX:
            return "IC FEVI Reducida"
        elif fevi <= config.FEVI_LIGERAMENTE_REDUCIDA_MAX: # Entre >40 y <=49
            return "IC FEVI Ligeramente Reducida"
        else: # FEVI > 49% (Preservada)
            if ai_vol is not None and ai_vol > config.AI_MIN_FA_CRITERIA: # (>34 ml/m2)
                # Considerar si ritmo sinusal vs FA afecta este umbral según infograma
                return "Alta probabilidad de IC FEVI Preservada"
            else:
                return "FEVI Preservada (valorar otras posibilidades si AI normal)"
    except Exception as e:
        log_message(f"Error calculando clasificación FEVI: {e}", "error", exc_info=True)
        return "Error en cálculo FEVI"
    # --- FIN: Marcador para localización de errores (Cálculo FEVI) ---


def estimar_presiones_llenado_vi(presiones_data: PresionesLlenadoVI, ai_data: MedidasAuriculas) -> str:
    # --- INICIO: Marcador para localización de errores (Cálculo Presiones Llenado) ---
    # Lógica basada en el algoritmo del infograma SEMI para E/A, E/e', Vol AI, Vel IT
    # Esta es una implementación parcial y simplificada.
    try:
        e_a = presiones_data.mitral_e_a_ratio
        e_e_prima = presiones_data.e_sobre_e_prima_ratio # Asumimos que este valor ya está calculado o ingresado
        ai_vol = ai_data.ai_vol_ml_m2
        it_vel = presiones_data.it_velocidad_max_ms

        if e_a is None:
            return "No valorables (E/A no disponible)"

        if e_a <= config.E_A_NORMAL_MAX: # E/A <= 0.8
            # Y si E/e' también es bajo (ej <8), sería más seguro "Normales"
            # Si E/A <= 0.8 pero E/e' > 14, es indeterminado/discordante
            return "Presiones de llenado normales (si datos consistentes)"
        
        if e_a >= config.E_A_ELEVADA_MIN: # E/A >= 2
            return "Presiones de llenado ELEVADAS (Patrón restrictivo)"

        # Caso E/A entre 0.8 y 2 (excluyendo 2)
        # Aplicar los 3 criterios adicionales:
        # 1. AI > 34 ml/m2
        # 2. E/e' > 14
        # 3. Vel IT > 2.8 m/s
        criterios_positivos = 0
        criterios_evaluables = 0

        if ai_vol is not None:
            criterios_evaluables += 1
            if ai_vol > config.AI_MIN_FA_CRITERIA: # >34 ml/m2
                criterios_positivos += 1
        
        if e_e_prima is not None:
            criterios_evaluables += 1
            if e_e_prima > config.E_E_PRIMA_CORTE: # >14
                criterios_positivos += 1
        
        if it_vel is not None:
            criterios_evaluables += 1
            if it_vel > config.IT_VELOCIDAD_CORTE: # >2.8 m/s
                criterios_positivos += 1

        if criterios_evaluables < 2: # No se pueden aplicar las reglas del infograma
             return "Indeterminadas (datos insuficientes para E/A 0.8-2)"
        
        if criterios_evaluables == 2:
            if criterios_positivos == 2:
                return "Presiones de llenado ELEVADAS"
            elif criterios_positivos == 0:
                 return "Presiones de llenado normales"
            else: # 1 positivo, 1 negativo
                 return "Indeterminadas (discordantes, valorar otras técnicas)"

        if criterios_evaluables == 3:
            if criterios_positivos >= 2:
                return "Presiones de llenado ELEVADAS"
            else: # 0 o 1 positivo
                return "Presiones de llenado normales"
        
        return "Indeterminadas (lógica no cubierta para E/A 0.8-2)"

    except Exception as e:
        log_message(f"Error estimando presiones de llenado VI: {e}", "error", exc_info=True)
        return "Error en cálculo Presiones Llenado"
    # --- FIN: Marcador para localización de errores (Cálculo Presiones Llenado) ---


def calcular_grado_vexus(vexus_data: VExUSScore) -> int:
    # --- INICIO: Marcador para localización de errores (Cálculo VExUS) ---
    # Lógica basada en el score VExUS (VCI > 2cm + patrones de flujo en VSH, VP, VIR)
    try:
        if not vexus_data.vci_patologica_vexus: # VCI <= 2cm
            return 0 # Grado 0 si VCI no está dilatada para el score

        patrones_severos = 0
        if vexus_data.patron_vena_suprahepatica == config.VSH_PATRONES[2]: # "Grave (Onda S invertida)"
            patrones_severos +=1
        if vexus_data.patron_vena_porta == config.VP_PATRONES[2]: # "Grave (Pulsatilidad >=50%, Monofásico S-D)"
            patrones_severos +=1
        if vexus_data.patron_vena_intrarrenal == config.VIR_PATRONES[2]: # "Grave (Monofásico S-D)"
            patrones_severos +=1
        
        if patrones_severos == 0: # VCI > 2cm pero ningún patrón severo
             # El infograma SEMI es un poco ambiguo aquí, si VCI > 2cm pero todo lo demás normal/leve.
             # VEXUS original: Grado 0 = VCI <2cm OR (VCI >=2cm AND no severe flow alterations OR <2 mild flow alterations)
             # Grado 1 = VCI >=2cm AND 1 severe flow OR >=2 mild flow alterations
             # Asumamos que si VCI > 2cm y 0 patrones severos -> Grado 1 (congestión leve si hay patrones leves)
             # Simplificando según el checklist "grado 0, 1, 2 ó 3". Si VCI > 2cm, mínimo es 1 si hay alguna alteración.
             # Si solo hay alteraciones leves, es Grado 1.
             # Para ser más precisos, necesitaríamos los patrones leves.
             # Si VCI > 2cm pero todo normal, es 0. Si VCI > 2cm y ALGO alterado, es >=1.
             # Por ahora, si no hay severos pero VCI >2cm, devolvemos 1 (asumiendo alguna alteración leve presente).
             # Esto necesita refinamiento para incluir patrones leves.
            return 1 # Placeholder, necesita más detalle para patrones leves
        elif patrones_severos == 1:
            return 2 # Grado 2 (un patrón severo)
        elif patrones_severos >= 2:
            return 3 # Grado 3 (dos o más patrones severos)
        
        return 0 # Default si VCI <= 2cm
    except Exception as e:
        log_message(f"Error calculando grado VExUS: {e}", "error", exc_info=True)
        return -1 # Indicar error
    # --- FIN: Marcador para localización de errores (Cálculo VExUS) ---

# Se añadirían más funciones de cálculo según sea necesario