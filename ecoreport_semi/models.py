# Creado por Alejandro Venegas Robles.
# En caso de incidencias, contactar con alejandro2196vr@gmail.com
# -*- coding: utf-8 -*-
"""
Modelos de datos (dataclasses) para el informe de ecocardioscopia.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict 
from datetime import datetime
import config # Para acceder a valores de referencia y otras constantes

# --- Claves para el diccionario parametro_no_valorado_flags ---
# Estas claves identificarán cada campo individual que puede ser "No Valorado"
# VI
P_VI_SEPTO = "vi_septo_mm"
P_VI_PARED_POST = "vi_pared_posterior_vi_mm"
P_VI_DTDVI = "vi_dtdvi_mm"
P_FEVI_CUALITATIVA = "fevi_cualitativa" 
P_FEVI_PORCENTAJE = "fevi_porcentaje"
# AI
P_AI_VOL_IDX = "ai_vol_ml_m2"
# VD
P_VD_DIAM_BASAL = "vd_diametro_basal_mm"
P_VD_TAPSE = "vd_tapse_mm"
# Valvulopatías
P_VALV_EST_AO = "valv_estenosis_aortica_sig"
P_VALV_INS_AO = "valv_insuficiencia_aortica_sig"
P_VALV_INS_MI = "valv_insuficiencia_mitral_sig"
P_VALV_INS_TR = "valv_insuficiencia_tricuspidea_sig"
# Presiones de Llenado
P_PRES_LLEN_E_A = "pres_llen_mitral_e_a_ratio"
P_PRES_LLEN_E_SEPTAL = "pres_llen_e_prima_septal_cms"
P_PRES_LLEN_E_LATERAL = "pres_llen_e_prima_lateral_cms"
P_PRES_LLEN_IT_VEL = "pres_llen_it_velocidad_max_ms"
P_PRES_LLEN_E_E_PRIMA_RATIO = "pres_llen_e_e_prima_ratio" # Constante que faltaba
# Derrame Pericárdico
P_DERR_PERIC_PRESENTE = "derr_peric_presente"
P_DERR_PERIC_CUANTIA = "derr_peric_cuantia_mm"
# Líneas B
P_LINEAS_B_PRESENTE = "lineas_b_presentes"
P_LINEAS_B_DESC = "lineas_b_descripcion_hallazgos"
# Derrame Pleural
P_DERR_PLEURAL_PRESENTE = "derr_pleural_presente"
P_DERR_PLEURAL_TIPO = "derr_pleural_tipo_cuantificacion"
P_DERR_PLEURAL_LOC = "derr_pleural_localizacion"
# VCI
P_VCI_DIAM = "vci_diametro_max_mm"
P_VCI_COLAPSO_RADIO = "vci_colapso_radio" # Para el grupo de radios >50% o <50%
P_VCI_MM_INSPIRACION = "vci_mm_inspiracion" # Para el campo de texto de mm en inspiración
# P_VCI_COLAPSO = "vci_colapso_inspiratorio_porcentaje" # Esta clave ya no se usa directamente para un campo de porcentaje
# VExUS
P_VEXUS_VCI_DILATADA = "vexus_vci_patologica_vexus"
P_VEXUS_VSH = "vexus_patron_vena_suprahepatica"
P_VEXUS_VP = "vexus_patron_vena_porta"
P_VEXUS_VIR = "vexus_patron_vena_intrarrenal"

# Helper function _format_valor (Corregido para manejar string en try-except)
def _format_valor(valor, unidad="", decimales=1, default_si_none="no medido"):
    """Formatea un valor numérico con su unidad y decimales especificados.
    Si el valor es None, retorna el texto por defecto."""
    if valor is None:
        return default_si_none
    try:
        val_float = float(valor) # Intentar convertir a float
        return f"{val_float:.{decimales}f}{unidad}"
    except (ValueError, TypeError): # Si no es convertible a float (ej. ya es un string formateado o texto)
        return f"{valor}{unidad}"


@dataclass
class DatosPaciente:
    nhc: str = ""
    nombre: str = ""
    apellidos: str = ""
    fecha_estudio: datetime = field(default_factory=datetime.now)

@dataclass
class MedidasVI:
    septo_iv_mm: Optional[float] = None
    pared_posterior_vi_mm: Optional[float] = None
    dtdvi_mm: Optional[float] = None
    fevi_porcentaje: Optional[float] = None
    fevi_cualitativa: Optional[str] = None

    @property
    def hipertrofia_vi_presente(self) -> str: # Cambiado a str para consistencia
        # Asumir sexo masculino si no se especifica, o crear lógica para pasarlo
        umbral_septo = getattr(config, 'SEPTUM_MAX_MASC', 11) 
        umbral_pared = getattr(config, 'PARED_POST_MAX_MASC', 11)
        
        presente = False
        detalles_hvi = []
        
        # Solo considerar si el valor NO es None
        if self.septo_iv_mm is not None:
            if self.septo_iv_mm > umbral_septo:
                presente = True
                detalles_hvi.append(f"Septo: {self.septo_iv_mm:.1f} mm")
        else: # Si es None pero se espera valoración (no marcado como NV globalmente)
            detalles_hvi.append("Septo no medido")


        if self.pared_posterior_vi_mm is not None:
            if self.pared_posterior_vi_mm > umbral_pared:
                presente = True
                detalles_hvi.append(f"Pared Posterior: {self.pared_posterior_vi_mm:.1f} mm")
        else:
            detalles_hvi.append("Pared Posterior no medida")

        # Si ambos son None (y por ende "no medido" está en detalles_hvi)
        if self.septo_iv_mm is None and self.pared_posterior_vi_mm is None:
            return "No valorado"

        if presente:
            return f"Sí ({', '.join(d for d in detalles_hvi if 'no medido' not in d)})" # Mostrar solo detalles de HVI
        
        # Si hay al menos una medida y no hay HVI
        if (self.septo_iv_mm is not None or self.pared_posterior_vi_mm is not None) and not presente:
             return "No"
        
        return "No valorado" # Caso por defecto si no entra en las otras lógicas


@dataclass
class MedidasAuriculas:
    ai_vol_ml_m2: Optional[float] = None

@dataclass
class MedidasVD:
    vd_diametro_basal_mm: Optional[float] = None
    tapse_mm: Optional[float] = None

    @property
    def vd_dilatado(self) -> str:
        if self.vd_diametro_basal_mm is None: return "No valorado"
        return "Sí" if self.vd_diametro_basal_mm > getattr(config, 'VD_DIAMETRO_BASAL_MAX', 42) else "No"

    @property
    def tapse_disminuido(self) -> str:
        if self.tapse_mm is None: return "No valorado"
        return "Sí" if self.tapse_mm < getattr(config, 'TAPSE_NORMAL_MIN', 17) else "No"

@dataclass
class Valvulopatias:
    estenosis_aortica_sig: bool = False
    insuficiencia_aortica_sig: bool = False
    insuficiencia_mitral_sig: bool = False
    insuficiencia_tricuspidea_sig: bool = False

@dataclass
class PresionesLlenadoVI:
    mitral_e_a_ratio: Optional[float] = None
    e_prima_septal_cms: Optional[float] = None
    e_prima_lateral_cms: Optional[float] = None
    it_velocidad_max_ms: Optional[float] = None
    e_sobre_e_prima_ratio: Optional[float] = None # Campo añadido

    @property
    def e_prima_media_cms(self) -> Optional[float]:
        valid_values = [v for v in [self.e_prima_septal_cms, self.e_prima_lateral_cms] if v is not None]
        if not valid_values: return None
        return sum(valid_values) / len(valid_values)

@dataclass
class DerramePericardico:
    presente: bool = False
    cuantia_mm: Optional[float] = None

    @property
    def clasificacion(self) -> str:
        if not self.presente: return "No"
        if self.cuantia_mm is None: return "Sí (cuantía no especificada)"
        leve_max = getattr(config, 'DERRPER_LEVE_MAX', 10)
        mod_max = getattr(config, 'DERRPER_MODERADO_MAX', 20)
        if self.cuantia_mm <= leve_max: return f"Sí, Leve ({self.cuantia_mm:.1f} mm)"
        elif self.cuantia_mm <= mod_max: return f"Sí, Moderado ({self.cuantia_mm:.1f} mm)"
        else: return f"Sí, Severo ({self.cuantia_mm:.1f} mm)"

@dataclass
class DerramePleural:
    presente: bool = False
    tipo_cuantificacion: Optional[str] = None
    localizacion: Optional[str] = None

    @property
    def descripcion(self) -> str:
        if not self.presente: return "No"
        desc = "Sí"
        if self.tipo_cuantificacion and self.tipo_cuantificacion.strip() != "": desc += f", {self.tipo_cuantificacion.lower()}"
        if self.localizacion and self.localizacion.strip() != "": desc += f" ({self.localizacion.lower()})"
        if desc == "Sí": desc += " (detalles no especificados)" # Si solo se marcó presente
        return desc

@dataclass
class LineasBEstudio:
    presentes: bool = False 
    descripcion_hallazgos: str = ""

@dataclass
class VenaCavaInferior: # Ya la tienes así, solo para confirmar
    diametro_max_mm: Optional[float] = None
    colapso_mayor_50: Optional[bool] = None  # True: >50%, False: <50%, None: no seleccionado/no valorado
    mm_inspiracion: Optional[float] = None   # mm en inspiración

    @property
    def hallazgos_vci(self) -> str:
        if self.diametro_max_mm is None and self.colapso_mayor_50 is None and self.mm_inspiracion is None:
            return "No valorada"
        
        partes = []
        if self.diametro_max_mm is not None:
            partes.append(f"Diámetro: {_format_valor(self.diametro_max_mm, ' mm')}")
        else: # Si no se midió el diámetro, pero sí el colapso
             if self.colapso_mayor_50 is not None or self.mm_inspiracion is not None:
                 partes.append("Diámetro: no medido")


        if self.colapso_mayor_50 is not None:
            partes.append(f"Colapso: {'>50%' if self.colapso_mayor_50 else '<50%'}")
        # El campo mm_inspiracion se añade si tiene valor, independientemente del radio de colapso
        if self.mm_inspiracion is not None:
            partes.append(f"Diámetro en inspiración: {_format_valor(self.mm_inspiracion, ' mm')}")
        elif self.colapso_mayor_50 is not None : # Si se valoró el colapso pero no los mm
            partes.append("Diámetro en inspiración: no medido")


        if not partes: # Si después de todo no hay nada que reportar (ej. solo Nones)
            return "No valorada"
        
        texto_base = ", ".join(partes) + "."

        # Añadir interpretación de PVC solo si tenemos diámetro Y colapso por radio
        if self.diametro_max_mm is not None and self.colapso_mayor_50 is not None:
            diam_pat_vci = getattr(config, 'VCI_DIAMETRO_PATOLOGICO_PVC', 21)
            # El infograma dice "<50%" para patológico si VCI > 21mm.
            # Entonces, colapso_mayor_50 == False (es decir, <50%) es el problemático.
            patologico_pvc = (self.diametro_max_mm > diam_pat_vci and not self.colapso_mayor_50)
            if patologico_pvc:
                texto_base += " Sugestiva de PVC elevada."
            else:
                texto_base += " No sugestiva de PVC elevada."
        return texto_base

    @property
    def hallazgos_vci(self) -> str:
        if self.diametro_max_mm is None and self.colapso_inspiratorio_porcentaje is None: return "No valorada"
        
        texto_diam = f"Diámetro: {_format_valor(self.diametro_max_mm, ' mm', default_si_none='no medido')}"
        texto_colapso = f"Colapso: {_format_valor(self.colapso_inspiratorio_porcentaje, '%', 0, default_si_none='no medido')}"
        texto = f"{texto_diam}, {texto_colapso}."

        if self.diametro_max_mm is not None and self.colapso_inspiratorio_porcentaje is not None:
            diam_pat_vci = getattr(config, 'VCI_DIAMETRO_PATOLOGICO_PVC', 21)
            colapso_min_normal_vci = getattr(config, 'VCI_COLAPSO_INSPIRATORIO_MIN_NORMAL_PVC', 50)
            patologico = (self.diametro_max_mm > diam_pat_vci and self.colapso_inspiratorio_porcentaje < colapso_min_normal_vci)
            if patologico: texto += " Sugestiva de PVC elevada."
            else: texto += " No sugestiva de PVC elevada."
        return texto

@dataclass
class VExUSScore:
    vci_patologica_vexus: bool = False
    patron_vena_suprahepatica: Optional[str] = None
    patron_vena_porta: Optional[str] = None
    patron_vena_intrarrenal: Optional[str] = None
    grado_vexus_calculado: Optional[int] = None


@dataclass
class InformeEcoCompleto:
    id_informe: str = field(default_factory=lambda: f"ECO-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}")
    realizado_por: str = ""
    comentarios_adicionales: str = ""
    
    paciente: DatosPaciente = field(default_factory=DatosPaciente)
    medidas_vi: MedidasVI = field(default_factory=MedidasVI)
    medidas_auriculas: MedidasAuriculas = field(default_factory=MedidasAuriculas)
    medidas_vd: MedidasVD = field(default_factory=MedidasVD)
    valvulopatias: Valvulopatias = field(default_factory=Valvulopatias)
    presiones_llenado: PresionesLlenadoVI = field(default_factory=PresionesLlenadoVI)
    derrame_pericardico: DerramePericardico = field(default_factory=DerramePericardico)
    derrame_pleural: DerramePleural = field(default_factory=DerramePleural)
    lineas_b: LineasBEstudio = field(default_factory=LineasBEstudio)
    vci: VenaCavaInferior = field(default_factory=VenaCavaInferior)
    vexus: VExUSScore = field(default_factory=VExUSScore)

    param_no_valorado_flags: Dict[str, bool] = field(default_factory=dict)