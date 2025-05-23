# Creado por Alejandro Venegas Robles.
# En caso de incidencias, contactar con alejandro2196vr@gmail.com
# -*- coding: utf-8 -*-
"""
Lógica para generar el texto del informe estructurado
basado en el modelo InformeEcoCompleto, en formato narrativo,
considerando campos vacíos y flags "No Valorado" por parámetro.
"""
from typing import Optional, List

from models import (InformeEcoCompleto, MedidasVI, MedidasAuriculas, PresionesLlenadoVI, VExUSScore,
                    P_VI_SEPTO, P_VI_PARED_POST, P_VI_DTDVI, P_FEVI_CUALITATIVA, P_FEVI_PORCENTAJE,
                    P_AI_VOL_IDX, P_VD_DIAM_BASAL, P_VD_TAPSE,
                    P_VALV_EST_AO, P_VALV_INS_AO, P_VALV_INS_MI, P_VALV_INS_TR,
                    P_PRES_LLEN_E_A, P_PRES_LLEN_E_SEPTAL, P_PRES_LLEN_E_LATERAL, P_PRES_LLEN_IT_VEL,
                    P_PRES_LLEN_E_E_PRIMA_RATIO, # Asegúrate que esta también esté en tu models.py
                    P_DERR_PERIC_PRESENTE, P_DERR_PERIC_CUANTIA,
                    P_LINEAS_B_PRESENTE, P_LINEAS_B_DESC,
                    P_DERR_PLEURAL_PRESENTE, P_DERR_PLEURAL_TIPO, P_DERR_PLEURAL_LOC,
                    P_VCI_DIAM, 
                    P_VCI_COLAPSO_RADIO, P_VCI_MM_INSPIRACION, # <<<--- USA ESTAS NUEVAS CONSTANTES
                    P_VEXUS_VCI_DILATADA, P_VEXUS_VSH, P_VEXUS_VP, P_VEXUS_VIR)
                    # Y ASEGÚRATE DE NO IMPORTAR P_VCI_COLAPSO (la antigua)
from .calculations import calcular_clasificacion_fevi, estimar_presiones_llenado_vi, calcular_grado_vexus
import config
from utils.error_handling import log_message

def _format_valor_narrativo(valor, unidad="", decimales=1, default_si_none="no se especificó", prefijo_valor=" "):
    """Formatea un valor para el informe narrativo, manejando None."""
    if valor is None:
        return default_si_none
    if isinstance(valor, float):
        return f"{prefijo_valor}{valor:.{decimales}f}{unidad}"
    if isinstance(valor, str) and valor == "": # Manejar string vacío como no especificado
        return default_si_none
    return f"{prefijo_valor}{valor}{unidad}"

def _construir_frase(componentes: List[str]) -> str:
    """Une componentes en una frase, manejando comas y 'y'."""
    componentes_validos = [c for c in componentes if c and c.strip() != ""]
    if not componentes_validos:
        return ""
    if len(componentes_validos) == 1:
        return componentes_validos[0]
    return ", ".join(componentes_validos[:-1]) + " y " + componentes_validos[-1]

# --- Funciones Helper por Sección para el Informe Narrativo ---

def _narrar_vi_dimensiones(informe: InformeEcoCompleto) -> Optional[str]:
    flags = informe.param_no_valorado_flags
    mvi = informe.medidas_vi
    frases_dim = []

    # Septo
    if flags.get(P_VI_SEPTO): frases_dim.append("grosor del septo interventricular no valorado")
    elif mvi.septo_iv_mm is not None: frases_dim.append(f"septo interventricular de{_format_valor_narrativo(mvi.septo_iv_mm, ' mm')}")
    
    # Pared Posterior
    if flags.get(P_VI_PARED_POST): frases_dim.append("grosor de la pared posterior no valorado")
    elif mvi.pared_posterior_vi_mm is not None: frases_dim.append(f"pared posterior de{_format_valor_narrativo(mvi.pared_posterior_vi_mm, ' mm')}")

    # DTDVI
    if flags.get(P_VI_DTDVI): frases_dim.append("DTDVI no valorado")
    elif mvi.dtdvi_mm is not None: frases_dim.append(f"diámetro telediastólico (DTDVI) de{_format_valor_narrativo(mvi.dtdvi_mm, ' mm')}")

    if not frases_dim: return None # No hay nada que decir de dimensiones

    texto_principal_dim = f"El ventrículo izquierdo presenta {_construir_frase(frases_dim)}."
    
    # Hipertrofia (basada en las propiedades del modelo que ya consideran los datos)
    # Solo se añade si hay datos para evaluarla y no se marcó como "no valorado" para septo/pared
    hvi_prop_texto = mvi.hipertrofia_vi_presente # "Sí (detalles)", "No", "No valorado"
    frase_hvi = ""
    if not (flags.get(P_VI_SEPTO) and flags.get(P_VI_PARED_POST)): # Si al menos uno no está NV
        if hvi_prop_texto and hvi_prop_texto != "No valorado":
            if "Sí" in hvi_prop_texto:
                frase_hvi = f" Se observan signos sugerentes de hipertrofia ventricular izquierda ({hvi_prop_texto.replace('Sí (','').replace(')','')})."
            elif "No" in hvi_prop_texto:
                frase_hvi = " No se observan signos de hipertrofia ventricular izquierda."
    
    return texto_principal_dim + frase_hvi

def _narrar_fevi(informe: InformeEcoCompleto) -> Optional[str]:
    flags = informe.param_no_valorado_flags
    mvi = informe.medidas_vi
    frases_fevi = []

    # FEVI Cualitativa
    if flags.get(P_FEVI_CUALITATIVA): frases_fevi.append("estimación visual cualitativa de FEVI no valorada")
    elif mvi.fevi_cualitativa and mvi.fevi_cualitativa != "No Estimar": # "No Estimar" se omite
        frases_fevi.append(f"una estimación visual cualitativa {mvi.fevi_cualitativa.lower()}")

    # FEVI Cuantitativa
    if flags.get(P_FEVI_PORCENTAJE): frases_fevi.append("FEVI cuantitativa no valorada")
    elif mvi.fevi_porcentaje is not None:
        frases_fevi.append(f"una FEVI cuantitativa del{_format_valor_narrativo(mvi.fevi_porcentaje, '%', 0)}")

    if not frases_fevi: return None

    texto_base_fevi = f"En cuanto a la función sistólica del ventrículo izquierdo, se objetiva {_construir_frase(frases_fevi)}."
    
    # Clasificación FEVI
    # Solo se añade si hay datos para la clasificación y la FEVI no está marcada como no valorada.
    # (Asumimos que calcular_clasificacion_fevi necesita al menos el porcentaje o cualitativa)
    if not (flags.get(P_FEVI_CUALITATIVA) and flags.get(P_FEVI_PORCENTAJE)):
        clasif_fevi = calcular_clasificacion_fevi(mvi, informe.medidas_auriculas)
        if clasif_fevi and clasif_fevi != "No valorada": # "No valorada" es el default de la función de cálculo
            return texto_base_fevi + f" Esto corresponde a una {clasif_fevi.lower()}."
    
    return texto_base_fevi

def _narrar_ai_volumen(informe: InformeEcoCompleto) -> Optional[str]:
    flags = informe.param_no_valorado_flags
    mai = informe.medidas_auriculas

    if flags.get(P_AI_VOL_IDX): return "El volumen de la aurícula izquierda no fue valorado."
    if mai.ai_vol_ml_m2 is not None:
        dilatada_texto = ""
        if mai.ai_vol_ml_m2 > getattr(config, 'AI_VOL_IDX_NORMAL_MAX_RS', 34): # Umbral de config
            dilatada_texto = ", sugestivo de dilatación auricular izquierda"
        return f"La aurícula izquierda presenta un volumen indexado de{_format_valor_narrativo(mai.ai_vol_ml_m2, ' ml/m²')}{dilatada_texto}."
    return None

def _narrar_vd_funcion(informe: InformeEcoCompleto) -> Optional[str]:
    flags = informe.param_no_valorado_flags
    mvd = informe.medidas_vd
    frases_vd = []

    # Diámetro Basal VD
    if flags.get(P_VD_DIAM_BASAL): frases_vd.append("diámetro basal del VD no valorado")
    elif mvd.vd_diametro_basal_mm is not None:
        dilatacion_prop = mvd.vd_dilatado # "Sí", "No", "No valorado"
        texto_diam = f"diámetro basal del ventrículo derecho de{_format_valor_narrativo(mvd.vd_diametro_basal_mm, ' mm')}"
        if dilatacion_prop == "Sí": texto_diam += " (dilatado)"
        elif dilatacion_prop == "No": texto_diam += " (no dilatado)"
        frases_vd.append(texto_diam)

    # TAPSE
    if flags.get(P_VD_TAPSE): frases_vd.append("TAPSE no valorado")
    elif mvd.tapse_mm is not None:
        tapse_prop = mvd.tapse_disminuido
        texto_tapse = f"TAPSE de{_format_valor_narrativo(mvd.tapse_mm, ' mm')}"
        if tapse_prop == "Sí": texto_tapse += " (disminuido, sugiere disfunción sistólica del VD)"
        elif tapse_prop == "No": texto_tapse += " (conservado)"
        frases_vd.append(texto_tapse)
    
    if not frases_vd: return None
    return f"Respecto al ventrículo derecho, se observa {_construir_frase(frases_vd)}."


def _narrar_valvulopatias(informe: InformeEcoCompleto) -> Optional[str]:
    flags = informe.param_no_valorado_flags
    valv = informe.valvulopatias
    sigs_encontradas = []
    no_valoradas = []

    if flags.get(P_VALV_EST_AO): no_valoradas.append("estenosis aórtica")
    elif valv.estenosis_aortica_sig: sigs_encontradas.append("estenosis aórtica significativa")
    
    if flags.get(P_VALV_INS_AO): no_valoradas.append("insuficiencia aórtica")
    elif valv.insuficiencia_aortica_sig: sigs_encontradas.append("insuficiencia aórtica significativa")

    if flags.get(P_VALV_INS_MI): no_valoradas.append("insuficiencia mitral")
    elif valv.insuficiencia_mitral_sig: sigs_encontradas.append("insuficiencia mitral significativa")

    if flags.get(P_VALV_INS_TR): no_valoradas.append("insuficiencia tricuspídea")
    elif valv.insuficiencia_tricuspidea_sig: sigs_encontradas.append("insuficiencia tricuspídea significativa")

    frases_valv = []
    if sigs_encontradas:
        frases_valv.append(f"Se identifican: {_construir_frase(sigs_encontradas)}.")
    elif not no_valoradas and not flags.get(P_VALV_EST_AO) and not flags.get(P_VALV_INS_AO) and not flags.get(P_VALV_INS_MI) and not flags.get(P_VALV_INS_TR): # Todos los checkboxes de valvulopatía fueron evaluados (no NV) y ninguno se marcó
        frases_valv.append("No se identificaron valvulopatías significativas.")
        
    if no_valoradas:
        frases_valv.append(f"La valoración detallada de {_construir_frase(no_valoradas)} no se realizó o no fue concluyente.")
        
    return " ".join(frases_valv) if frases_valv else None


def _narrar_presiones_llenado(informe: InformeEcoCompleto) -> Optional[str]:
    flags = informe.param_no_valorado_flags
    pres_llen = informe.presiones_llenado
    
    # Comprobar si todos los parámetros individuales de presiones de llenado están marcados como NV
    todos_nv = all(flags.get(k, False) for k in [P_PRES_LLEN_E_A, P_PRES_LLEN_E_SEPTAL, P_PRES_LLEN_E_LATERAL, P_PRES_LLEN_IT_VEL])
    # Comprobar si todos los parámetros individuales de presiones de llenado son None (no introducidos)
    todos_none = all(getattr(pres_llen, attr) is None for attr in ["mitral_e_a_ratio", "e_prima_septal_cms", "e_prima_lateral_cms", "it_velocidad_max_ms"])


    if todos_nv: return "La estimación de presiones de llenado del VI no fue valorada."
    if todos_none and not any(flags.get(k, False) for k in [P_PRES_LLEN_E_A, P_PRES_LLEN_E_SEPTAL, P_PRES_LLEN_E_LATERAL, P_PRES_LLEN_IT_VEL]):
        # Ningún dato introducido y ninguno marcado como NV individualmente
        return None # Omitir la sección si no hay datos ni se marcó como NV

    texto_estimacion = estimar_presiones_llenado_vi(pres_llen, informe.medidas_auriculas)
    
    frase_resultado = ""
    if texto_estimacion and "Error" not in texto_estimacion and texto_estimacion != "No valoradas (E/A no disponible)":
        frase_resultado = f"La estimación de las presiones de llenado del ventrículo izquierdo sugiere: {texto_estimacion.lower()}."
    
    # Añadir detalles de los parámetros si fueron valorados
    detalles_params = []
    if not flags.get(P_PRES_LLEN_E_A) and pres_llen.mitral_e_a_ratio is not None:
        detalles_params.append(f"ratio E/A mitral de{_format_valor_narrativo(pres_llen.mitral_e_a_ratio, decimales=2)}")
    if not flags.get(P_PRES_LLEN_E_SEPTAL) and pres_llen.e_prima_septal_cms is not None:
        detalles_params.append(f"e' septal de{_format_valor_narrativo(pres_llen.e_prima_septal_cms, ' cm/s')}")
    if not flags.get(P_PRES_LLEN_E_LATERAL) and pres_llen.e_prima_lateral_cms is not None:
        detalles_params.append(f"e' lateral de{_format_valor_narrativo(pres_llen.e_prima_lateral_cms, ' cm/s')}")
    if not flags.get(P_PRES_LLEN_IT_VEL) and pres_llen.it_velocidad_max_ms is not None:
        detalles_params.append(f"velocidad máxima de IT de{_format_valor_narrativo(pres_llen.it_velocidad_max_ms, ' m/s')}")

    if frase_resultado and detalles_params:
        return f"{frase_resultado} Basado en: {_construir_frase(detalles_params)}."
    elif frase_resultado:
        return frase_resultado
    elif detalles_params: # Hay datos pero la estimación no fue concluyente
        return f"Se valoraron los siguientes parámetros para presiones de llenado: {_construir_frase(detalles_params)}, sin una estimación concluyente."
    
    return None


def _narrar_derrames_y_lineasb(informe: InformeEcoCompleto) -> Optional[str]:
    flags = informe.param_no_valorado_flags
    frases_total = []

    # Derrame Pericárdico
    dp_presente_nv = flags.get(P_DERR_PERIC_PRESENTE, False)
    dp_cuantia_nv = flags.get(P_DERR_PERIC_CUANTIA, False)
    dper = informe.derrame_pericardico
    
    if dp_presente_nv and dp_cuantia_nv : # Ambos NV
        frases_total.append("Derrame pericárdico no valorado.")
    else:
        if dper.presente:
            clasif_texto = dper.clasificacion.lower().replace("sí, ", "") # "leve (x mm)"
            frases_total.append(f"Se observa derrame pericárdico {clasif_texto}.")
        elif not dp_presente_nv : # Se valoró "presente" y fue False
            frases_total.append("No se objetiva derrame pericárdico.")
        # Si "presente" es NV pero "cuantía" no, o viceversa, es un estado mixto un poco raro.
        # Se podría refinar, pero por ahora si uno de los dos se valoró, se intenta describir.

    # Líneas B
    lb_presente_nv = flags.get(P_LINEAS_B_PRESENTE, False)
    lb_desc_nv = flags.get(P_LINEAS_B_DESC, False)
    lineas_b_obj = informe.lineas_b

    if lb_presente_nv and lb_desc_nv:
        frases_total.append("Líneas B no valoradas.")
    else:
        if lineas_b_obj.presentes:
            texto_lb = "Presencia de líneas B"
            if not lb_desc_nv and lineas_b_obj.descripcion_hallazgos and lineas_b_obj.descripcion_hallazgos.strip() != "":
                texto_lb += f": {lineas_b_obj.descripcion_hallazgos.strip()}."
            else:
                texto_lb += " sugestivas de congestión intersticial."
            frases_total.append(texto_lb)
        elif not lb_presente_nv: # Se valoró y no hay
            frases_total.append("No se identifican líneas B patológicas.")

    # Derrame Pleural
    dpl_presente_nv = flags.get(P_DERR_PLEURAL_PRESENTE, False)
    dpl_tipo_nv = flags.get(P_DERR_PLEURAL_TIPO, False)
    dpl_loc_nv = flags.get(P_DERR_PLEURAL_LOC, False)
    dple = informe.derrame_pleural

    if dpl_presente_nv and dpl_tipo_nv and dpl_loc_nv:
        frases_total.append("Derrame pleural no valorado.")
    else:
        if dple.presente:
            texto_dple = "Derrame pleural"
            detalles_dple = []
            if not dpl_tipo_nv and dple.tipo_cuantificacion: detalles_dple.append(dple.tipo_cuantificacion.lower())
            if not dpl_loc_nv and dple.localizacion: detalles_dple.append(dple.localizacion.lower())
            if detalles_dple: texto_dple += f" {' y '.join(detalles_dple)}."
            else: texto_dple += " presente (detalles no especificados)."
            frases_total.append(texto_dple)
        elif not dpl_presente_nv:
            frases_total.append("No se evidencia derrame pleural.")
            
    return " ".join(frases_total) if frases_total else None


def _narrar_congestion_sistemica(informe: InformeEcoCompleto) -> Optional[str]:
    flags = informe.param_no_valorado_flags
    frases_sist = []
    vci = informe.vci # Acceder al objeto VenaCavaInferior del informe

    # VCI
    vci_diam_nv = flags.get(P_VCI_DIAM, False)
    # Para el colapso, ahora son dos campos en el modelo: colapso_mayor_50 (bool) y mm_inspiracion (float)
    # y dos flags de "No Valorado": P_VCI_COLAPSO_RADIO y P_VCI_MM_INSPIRACION
    vci_col_radio_nv = flags.get(P_VCI_COLAPSO_RADIO, False)
    vci_mm_insp_nv = flags.get(P_VCI_MM_INSPIRACION, False)

    # Si todos los componentes de la VCI están marcados como NV
    if vci_diam_nv and vci_col_radio_nv and vci_mm_insp_nv:
        frases_sist.append("Vena cava inferior no valorada.")
    else:
        # La propiedad hallazgos_vci en models.VenaCavaInferior ya debería estar construyendo
        # un texto descriptivo adecuado usando vci.diametro_max_mm, vci.colapso_mayor_50, y vci.mm_inspiracion.
        # Solo necesitamos asegurar que si un componente individual fue marcado NV, se refleje.

        partes_vci_narradas = []
        # Diámetro
        if vci_diam_nv:
            partes_vci_narradas.append("diámetro máximo no valorado")
        elif vci.diametro_max_mm is not None:
            partes_vci_narradas.append(f"diámetro máximo de {_format_valor_narrativo(vci.diametro_max_mm, ' mm', prefijo_valor='')}")

        # Colapso (Radio)
        if vci_col_radio_nv:
            partes_vci_narradas.append("colapso inspiratorio no valorado")
        elif vci.colapso_mayor_50 is not None:
            partes_vci_narradas.append(f"colapso inspiratorio {'>50%' if vci.colapso_mayor_50 else '<50%'}")

        # mm Inspiración
        if vci_mm_insp_nv:
            partes_vci_narradas.append("diámetro en inspiración no valorado")
        elif vci.mm_inspiracion is not None:
            partes_vci_narradas.append(f"diámetro en inspiración de {_format_valor_narrativo(vci.mm_inspiracion, ' mm', prefijo_valor='')}")

        if partes_vci_narradas:
            texto_vci = f"La vena cava inferior presenta {_construir_frase(partes_vci_narradas)}."
            # Añadir interpretación de PVC si hay suficientes datos y no están NV
            if not vci_diam_nv and not vci_col_radio_nv and \
               vci.diametro_max_mm is not None and vci.colapso_mayor_50 is not None:
                diam_pat_vci = getattr(config, 'VCI_DIAMETRO_PATOLOGICO_PVC', 21)
                colapso_problematico = not vci.colapso_mayor_50 # <50% es problemático si VCI dilatada

                if vci.diametro_max_mm > diam_pat_vci and colapso_problematico:
                    texto_vci += " Sugestiva de PVC elevada."
                else:
                    texto_vci += " No sugestiva de PVC elevada."
            frases_sist.append(texto_vci)
        elif not (vci_diam_nv and vci_col_radio_nv and vci_mm_insp_nv): # Si no todos NV pero no se pudo narrar
             frases_sist.append("Valoración de la VCI incompleta.")


    # VExUS (esta parte debería estar bien si las P_... para VExUS son correctas)
    vexus_vci_dil_nv = flags.get(P_VEXUS_VCI_DILATADA, False)
    vexus_vsh_nv = flags.get(P_VEXUS_VSH, False)
    vexus_vp_nv = flags.get(P_VEXUS_VP, False)
    vexus_vir_nv = flags.get(P_VEXUS_VIR, False)

    if all([vexus_vci_dil_nv, vexus_vsh_nv, vexus_vp_nv, vexus_vir_nv]):
        frases_sist.append("Score VExUS no calculado (parámetros no valorados).")
    else:
        # Asegurarse que el modelo VExUS tiene los datos antes de calcular
        if not vexus_vci_dil_nv : informe.vexus.vci_patologica_vexus # Ya debería estar en el modelo
        # ... (los patrones venosos ya deberían estar en informe.vexus desde la UI)

        grado_calc = calcular_grado_vexus(informe.vexus) # La función de cálculo usa los datos del modelo
        if grado_calc is not None and grado_calc != -1: # -1 podría indicar error/insuficiente
            frases_sist.append(f"El score VExUS para congestión sistémica es de grado {grado_calc}.")
            if grado_calc > 0:
                detalles_vexus = []
                if not vexus_vsh_nv and informe.vexus.patron_vena_suprahepatica and informe.vexus.patron_vena_suprahepatica != getattr(config, 'VSH_PATRONES', [""])[0]:
                    detalles_vexus.append(f"V. Suprahepática con patrón {informe.vexus.patron_vena_suprahepatica.split('(')[0].lower().strip()}")
                if not vexus_vp_nv and informe.vexus.patron_vena_porta and informe.vexus.patron_vena_porta != getattr(config, 'VP_PATRONES', [""])[0]:
                    detalles_vexus.append(f"V. Porta con patrón {informe.vexus.patron_vena_porta.split('(')[0].lower().strip()}")
                if not vexus_vir_nv and informe.vexus.patron_vena_intrarrenal and informe.vexus.patron_vena_intrarrenal != getattr(config, 'VIR_PATRONES', [""])[0]:
                    detalles_vexus.append(f"V. Intrarrenal con patrón {informe.vexus.patron_vena_intrarrenal.split('(')[0].lower().strip()}")
                if detalles_vexus: frases_sist.append(f"Hallazgos contribuyentes: {_construir_frase(detalles_vexus)}.")
        elif not all([vexus_vci_dil_nv, vexus_vsh_nv, vexus_vp_nv, vexus_vir_nv]):
             frases_sist.append("Datos para VExUS incompletos para un cálculo definitivo.")

    return " ".join(frases_sist) if frases_sist else None


def generar_informe_texto(informe: InformeEcoCompleto) -> str:
    try:
        parrafos_finales = []
        parrafos_finales.append("INFORME DE ECOCARDIOSCOPIA CLÍNICA A PIE DE CAMA")
        parrafos_finales.append("==============================================")

        if informe.realizado_por and informe.realizado_por.strip() != "":
            parrafos_finales.append(f"Realizado por: {informe.realizado_por.strip()}\n")
        
        # --- Construcción del cuerpo del informe ---
        cuerpo_informe = []
        
        parrafo_vi = _narrar_vi_dimensiones(informe)
        if parrafo_vi: cuerpo_informe.append(parrafo_vi)
        
        parrafo_fevi = _narrar_fevi(informe) # FEVI ahora es parte de _narrar_vi, o puede ser separada
        # Si _narrar_vi ya incluye FEVI, no llamar a _narrar_fevi por separado.
        # Ajustado arriba: _narrar_vi incluye dimensiones y _narrar_fevi la función.
        if parrafo_fevi: cuerpo_informe.append(parrafo_fevi)
        
        parrafo_ai = _narrar_ai_volumen(informe)
        if parrafo_ai: cuerpo_informe.append(parrafo_ai)
        
        parrafo_vd = _narrar_vd_funcion(informe)
        if parrafo_vd: cuerpo_informe.append(parrafo_vd)
        
        parrafo_valv = _narrar_valvulopatias(informe)
        if parrafo_valv: cuerpo_informe.append(parrafo_valv)
        
        parrafo_pres_llen = _narrar_presiones_llenado(informe)
        if parrafo_pres_llen: cuerpo_informe.append(parrafo_pres_llen)
        
        parrafo_derrames_lineasb = _narrar_derrames_y_lineasb(informe) # Combina varios ahora
        if parrafo_derrames_lineasb: cuerpo_informe.append(parrafo_derrames_lineasb)
        
        parrafo_cong_sist = _narrar_congestion_sistemica(informe)
        if parrafo_cong_sist: cuerpo_informe.append(parrafo_cong_sist)

        if cuerpo_informe: # Si hay algún hallazgo que reportar
            parrafos_finales.append("\n--- HALLAZGOS ECOCARDIOGRÁFICOS ---")
            parrafos_finales.append("\n\n".join(cuerpo_informe)) # Unir párrafos de hallazgos con doble salto
        else: # Si todo se omitió o estaba NV y no generó texto.
            parrafos_finales.append("\nNo se detallaron hallazgos ecocardiográficos específicos o todos los apartados fueron omitidos/no valorados.")


        if informe.comentarios_adicionales and informe.comentarios_adicionales.strip() != "":
            parrafos_finales.append("\n\n--- CONCLUSIÓN / COMENTARIOS ADICIONALES ---")
            parrafos_finales.append(informe.comentarios_adicionales.strip())
        
        parrafos_finales.append("\n==============================================")
        
        log_message("Informe de texto en formato párrafo (nueva lógica) generado.", "info")
        
        return "\n".join(parrafos_finales).strip()

    except Exception as e:
        log_message(f"Error crítico generando informe (nueva lógica): {e}", "error", exc_info=True)
        return f"ERROR AL GENERAR EL INFORME:\n{e}\n\nConsulte el log."