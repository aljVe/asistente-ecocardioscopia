# Creado por Alejandro Venegas Robles.
# En caso de incidencias, contactar con alejandro2196vr@gmail.com
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QLabel,
                             QLineEdit, QFormLayout, QCheckBox, QComboBox,
                             QScrollArea, QRadioButton, QHBoxLayout, QButtonGroup)
from PyQt5.QtGui import QDoubleValidator, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from functools import partial
from typing import Tuple, Dict, Any, Optional, List 
import os

from models import (InformeEcoCompleto,
                    P_VI_SEPTO, P_VI_PARED_POST, P_VI_DTDVI, P_FEVI_CUALITATIVA, P_FEVI_PORCENTAJE,
                    P_AI_VOL_IDX, P_VD_DIAM_BASAL, P_VD_TAPSE,
                    P_VALV_EST_AO, P_VALV_INS_AO, P_VALV_INS_MI, P_VALV_INS_TR,
                    P_PRES_LLEN_E_A, P_PRES_LLEN_E_SEPTAL, P_PRES_LLEN_E_LATERAL, P_PRES_LLEN_IT_VEL,
                    P_PRES_LLEN_E_E_PRIMA_RATIO,
                    P_DERR_PERIC_PRESENTE, P_DERR_PERIC_CUANTIA,
                    P_LINEAS_B_PRESENTE, P_LINEAS_B_DESC,
                    P_DERR_PLEURAL_PRESENTE, P_DERR_PLEURAL_TIPO, P_DERR_PLEURAL_LOC,
                    P_VCI_DIAM, P_VCI_COLAPSO_RADIO, P_VCI_MM_INSPIRACION, # Claves VCI actualizadas
                    P_VEXUS_VCI_DILATADA, P_VEXUS_VSH, P_VEXUS_VP, P_VEXUS_VIR)
import config
from utils.error_handling import log_message

class DatosEcoTab(QWidget):
    FEVI_CUALITATIVA_OPCIONES = ["No Estimar", "Preservada", "Ligeramente deprimida", "Severamente deprimida"]
    modelo_modificado = pyqtSignal()
    TARGET_IMAGE_WIDTH = 350 

    def __init__(self, modelo_informe: InformeEcoCompleto, parent=None):
        super().__init__(parent)
        self.modelo_informe = modelo_informe
        self.numeric_validator = QDoubleValidator(self)
        self.numeric_validator.setNotation(QDoubleValidator.StandardNotation)
        self.percentage_validator = QDoubleValidator(0, 100, 2, self)
        self.percentage_validator.setNotation(QDoubleValidator.StandardNotation)
        self.param_controls: Dict[str, Dict[str, Any]] = {}
        self._init_ui()
        self.cargar_modelo_en_ui()
        log_message("Pestaña DatosEcoTab (simplificada y con imagen) inicializada.", "debug")

    def _safe_text_to_float(self, qlineedit: QLineEdit) -> Optional[float]:
        object_name = qlineedit.objectName() if qlineedit.objectName() else "QLineEdit"
        text = qlineedit.text().strip().replace(',', '.')
        if not text: return None
        try: return float(text)
        except ValueError:
            log_message(f"Error de conversión a float: '{text}' en '{object_name}'", "warning")
            return None

    def _crear_linea_parametro(self, param_key: str, widget_entrada: QWidget, unidad_text: Optional[str] = None, button_group_for_radios: Optional[QButtonGroup] = None) -> QHBoxLayout:
        line_layout = QHBoxLayout()
        line_layout.setContentsMargins(0,0,0,0)
        line_layout.setSpacing(5)
        nv_checkbox = QCheckBox("NV")
        nv_checkbox.setToolTip(f"Marcar si este parámetro ({param_key}) no fue valorado.")
        line_layout.addWidget(nv_checkbox)
        line_layout.addWidget(widget_entrada)
        if unidad_text:
            line_layout.addWidget(QLabel(unidad_text))
        line_layout.addStretch(1)
        self.param_controls[param_key] = {"input": widget_entrada, "nv_check": nv_checkbox}
        if button_group_for_radios:
             self.param_controls[param_key]["button_group"] = button_group_for_radios
        nv_checkbox.stateChanged.connect(partial(self._on_nv_checkbox_changed, param_key))
        if isinstance(widget_entrada, QLineEdit): widget_entrada.editingFinished.connect(self.actualizar_modelo_y_emitir)
        elif isinstance(widget_entrada, QComboBox): widget_entrada.currentIndexChanged.connect(self.actualizar_modelo_y_emitir)
        elif isinstance(widget_entrada, QCheckBox) and widget_entrada != nv_checkbox : widget_entrada.stateChanged.connect(self.actualizar_modelo_y_emitir)
        elif button_group_for_radios : button_group_for_radios.buttonClicked.connect(self.actualizar_modelo_y_emitir)
        return line_layout
        
    def _on_nv_checkbox_changed(self, param_key: str, state: int):
        controls = self.param_controls.get(param_key)
        if not controls: return
        is_nv = (state == Qt.Checked)
        input_widget_or_container = controls["input"]
        
        # Habilitar/deshabilitar el widget de entrada principal o los componentes de un contenedor
        if isinstance(input_widget_or_container, QButtonGroup): # Caso especial para FEVI Cualitativa y otros grupos de radio
            for rb in input_widget_or_container.buttons():
                rb.setEnabled(not is_nv)
            if is_nv: # Resetear a "No Estimar" o similar
                if param_key == P_FEVI_CUALITATIVA: self.fevi_radio_ninguna.setChecked(True)
                elif param_key == P_DERR_PERIC_PRESENTE: self.derr_per_radio_ausente.setChecked(True) # Asume que "Ausente" es el default
                elif param_key == P_LINEAS_B_PRESENTE: self.lineas_b_radio_ausente.setChecked(True)
                elif param_key == P_DERR_PLEURAL_PRESENTE: self.derr_pleural_radio_ausente.setChecked(True)
                elif param_key == P_VCI_COLAPSO_RADIO: # Reset VCI colapso radios
                    self.vci_colapso_radio_mayor.setAutoExclusive(False); self.vci_colapso_radio_mayor.setChecked(False); self.vci_colapso_radio_mayor.setAutoExclusive(True)
                    self.vci_colapso_radio_menor.setAutoExclusive(False); self.vci_colapso_radio_menor.setChecked(False); self.vci_colapso_radio_menor.setAutoExclusive(True)

        elif isinstance(input_widget_or_container, QWidget) and not isinstance(input_widget_or_container, (QLineEdit, QComboBox, QCheckBox)):
             # Podría ser un QWidget contenedor (ej. para FEVI cualitativa o VCI colapso)
            for child_widget in input_widget_or_container.findChildren(QWidget): # Deshabilitar todos los hijos
                if not isinstance(child_widget, QLabel): # No deshabilitar QLabel
                    child_widget.setEnabled(not is_nv)
            if is_nv and param_key == P_FEVI_CUALITATIVA: self.fevi_radio_ninguna.setChecked(True)
        else: # Es un widget de entrada simple
            input_widget_or_container.setEnabled(not is_nv)
        
        if is_nv: # Limpiar valor si se marca NV
            if isinstance(input_widget_or_container, QLineEdit): input_widget_or_container.clear()
            elif isinstance(input_widget_or_container, QComboBox): input_widget_or_container.setCurrentIndex(0)
            elif isinstance(input_widget_or_container, QCheckBox): input_widget_or_container.setChecked(False)
            # Limpieza de QButtonGroup ya manejada arriba
        
        # Si este NV afecta a otros campos (como un "Presente" que controla "Cuantía")
        # Llamar a _on_sub_checkbox_changed para actualizar el estado de los dependientes.
        # Esto es un poco complejo porque _on_sub_checkbox_changed también es llamado por el stateChanged del "Presente".
        # Necesitamos evitar llamadas recursivas o asegurar que el estado es consistente.
        # Por ahora, el _on_sub_checkbox_changed debería verificar el estado NV de su control primario.

        self.actualizar_modelo_y_emitir()

    def actualizar_modelo_y_emitir(self, *args):
        self.actualizar_modelo()
        self.modelo_modificado.emit()

    def _on_sub_checkbox_changed(self, master_checkbox_or_radio_group: QWidget, secondary_param_key: str, affected_secondary_widgets: List[QWidget]):
        # Determinar si el control maestro permite que los secundarios estén activos
        enable_secondaries = False
        master_is_nv = False

        # Encontrar el checkbox NV del control maestro
        for pk, ctrl_dict in self.param_controls.items():
            if ctrl_dict["input"] == master_checkbox_or_radio_group or ctrl_dict.get("button_group") == master_checkbox_or_radio_group:
                master_is_nv = ctrl_dict["nv_check"].isChecked()
                break
        
        if not master_is_nv: # Solo proceder si el control maestro no está marcado como NV
            if isinstance(master_checkbox_or_radio_group, QCheckBox): # Ej. Valvulopatía Sig.
                enable_secondaries = master_checkbox_or_radio_group.isChecked()
            elif isinstance(master_checkbox_or_radio_group, QButtonGroup): # Ej. Derrame Presente/Ausente
                # Asumimos que "Presente" es el que habilita
                for rb in master_checkbox_or_radio_group.buttons():
                    if rb.text().lower().startswith("presente") and rb.isChecked():
                        enable_secondaries = True
                        break
        
        for widget_sec in affected_secondary_widgets:
            widget_sec.setEnabled(enable_secondaries)
            # Habilitar/deshabilitar el checkbox NV del widget secundario
            sec_nv_check = None
            for pk_sec, ctrl_dict_sec in self.param_controls.items():
                if ctrl_dict_sec["input"] == widget_sec:
                    sec_nv_check = ctrl_dict_sec["nv_check"]
                    break
            if sec_nv_check:
                sec_nv_check.setEnabled(enable_secondaries)
                if not enable_secondaries: # Si el secundario se deshabilita, desmarcar su NV y limpiar
                    sec_nv_check.setChecked(False) 
            
            if not enable_secondaries:
                if isinstance(widget_sec, QLineEdit): widget_sec.clear()
                elif isinstance(widget_sec, QComboBox): widget_sec.setCurrentIndex(0)
        
        self.actualizar_modelo_y_emitir()


    def _init_ui(self):
        # ... (main_tab_layout, scroll_area, scroll_content_widget, content_layout como antes) ...
        # ... (SHORT_LINE_EDIT_WIDTH como antes) ...
        # === La estructura interna de _init_ui para crear los QGroupBox y QFormLayouts
        #     CON LOS CAMPOS Y SUS _crear_linea_parametro DEBE SER LA MISMA QUE TE DI
        #     EN LA RESPUESTA ANTERIOR (la que ajustaba los QLineEdit y los radios NV al lado).
        #     Solo asegúrate de que las claves P_... sean correctas y que los widgets
        #     se creen y se añadan al param_controls.
        #     VOY A REPETIR LA ESTRUCTURA CON LAS CLAVES CORRECTAS Y LA NUEVA VCI:

        main_tab_layout = QHBoxLayout(self); main_tab_layout.setContentsMargins(5,5,5,5)
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True); scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_content_widget = QWidget(); content_layout = QVBoxLayout(self.scroll_content_widget)
        content_layout.setSpacing(15); content_layout.setContentsMargins(5,5,10,5)
        SHORT_LINE_EDIT_WIDTH = 70

        # === Eco Básica ===
        eco_basica_group = QGroupBox("Eco Básica (VI, AI, VD)"); eco_basica_form = QFormLayout(); eco_basica_form.setLabelAlignment(Qt.AlignLeft); eco_basica_form.setRowWrapPolicy(QFormLayout.WrapLongRows); eco_basica_form.setSpacing(8)
        self.septo_iv_edit = QLineEdit(); self.septo_iv_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.septo_iv_edit.setValidator(self.numeric_validator); self.septo_iv_edit.setPlaceholderText("mm")
        eco_basica_form.addRow("Septo IV:", self._crear_linea_parametro(P_VI_SEPTO, self.septo_iv_edit, "mm"))
        self.pared_posterior_edit = QLineEdit(); self.pared_posterior_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.pared_posterior_edit.setValidator(self.numeric_validator); self.pared_posterior_edit.setPlaceholderText("mm")
        eco_basica_form.addRow("Pared Post. VI:", self._crear_linea_parametro(P_VI_PARED_POST, self.pared_posterior_edit, "mm"))
        self.dtdvi_edit = QLineEdit(); self.dtdvi_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.dtdvi_edit.setValidator(self.numeric_validator); self.dtdvi_edit.setPlaceholderText("mm")
        eco_basica_form.addRow("DTDVI:", self._crear_linea_parametro(P_VI_DTDVI, self.dtdvi_edit, "mm"))
        fevi_estim_layout_radios = QHBoxLayout(); fevi_estim_layout_radios.setContentsMargins(0,0,0,0)
        self.fevi_radio_group = QButtonGroup(self)
        self.fevi_radio_ninguna = QRadioButton("No Estimar"); self.fevi_radio_ninguna.setChecked(True)
        self.fevi_radio_preservada = QRadioButton("Preservada"); self.fevi_radio_ligera = QRadioButton("Ligeramente Dep."); self.fevi_radio_severa = QRadioButton("Severamente Dep.")
        for rb in [self.fevi_radio_ninguna, self.fevi_radio_preservada, self.fevi_radio_ligera, self.fevi_radio_severa]: fevi_estim_layout_radios.addWidget(rb); self.fevi_radio_group.addButton(rb)
        fevi_estim_layout_radios.addStretch(); fevi_radios_widget_container = QWidget(); fevi_radios_widget_container.setLayout(fevi_estim_layout_radios)
        eco_basica_form.addRow("Estimación Visual FEVI:", self._crear_linea_parametro(P_FEVI_CUALITATIVA, fevi_radios_widget_container, button_group_for_radios=self.fevi_radio_group))
        self.fevi_edit = QLineEdit(); self.fevi_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.fevi_edit.setValidator(self.percentage_validator); self.fevi_edit.setPlaceholderText("%")
        eco_basica_form.addRow("FEVI Cuantitativa:", self._crear_linea_parametro(P_FEVI_PORCENTAJE, self.fevi_edit, "%"))
        self.vol_ai_idx_edit = QLineEdit(); self.vol_ai_idx_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.vol_ai_idx_edit.setValidator(self.numeric_validator); self.vol_ai_idx_edit.setPlaceholderText("ml/m²")
        eco_basica_form.addRow("Volumen AI Indexado:", self._crear_linea_parametro(P_AI_VOL_IDX, self.vol_ai_idx_edit, "ml/m²"))
        self.diam_basal_vd_edit = QLineEdit(); self.diam_basal_vd_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.diam_basal_vd_edit.setValidator(self.numeric_validator); self.diam_basal_vd_edit.setPlaceholderText("mm")
        eco_basica_form.addRow("Diámetro Basal VD:", self._crear_linea_parametro(P_VD_DIAM_BASAL, self.diam_basal_vd_edit, "mm"))
        self.tapse_edit = QLineEdit(); self.tapse_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.tapse_edit.setValidator(self.numeric_validator); self.tapse_edit.setPlaceholderText("mm")
        eco_basica_form.addRow("TAPSE:", self._crear_linea_parametro(P_VD_TAPSE, self.tapse_edit, "mm"))
        eco_basica_group.setLayout(eco_basica_form); content_layout.addWidget(eco_basica_group)

        # === Eco Avanzada ===
        eco_avanzada_group = QGroupBox("Eco Avanzada (Valvulopatías, Presiones, Pericardio)"); eco_avanzada_form = QFormLayout(); eco_avanzada_form.setLabelAlignment(Qt.AlignLeft); eco_avanzada_form.setRowWrapPolicy(QFormLayout.WrapLongRows); eco_avanzada_form.setSpacing(8)
        self.est_ao_check = QCheckBox("Estenosis Aórtica Sig."); eco_avanzada_form.addRow("EAo Sig.:", self._crear_linea_parametro(P_VALV_EST_AO, self.est_ao_check))
        self.ins_ao_check = QCheckBox("Insuficiencia Aórtica Sig."); eco_avanzada_form.addRow("IAo Sig.:", self._crear_linea_parametro(P_VALV_INS_AO, self.ins_ao_check))
        self.ins_mi_check = QCheckBox("Insuficiencia Mitral Sig."); eco_avanzada_form.addRow("IM Sig.:", self._crear_linea_parametro(P_VALV_INS_MI, self.ins_mi_check))
        self.ins_tr_check = QCheckBox("Insuficiencia Tricuspídea Sig."); eco_avanzada_form.addRow("IT Sig.:", self._crear_linea_parametro(P_VALV_INS_TR, self.ins_tr_check))
        self.ratio_e_a_edit = QLineEdit(); self.ratio_e_a_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.ratio_e_a_edit.setValidator(self.numeric_validator); self.ratio_e_a_edit.setPlaceholderText("ej: 0.8")
        eco_avanzada_form.addRow("Ratio E/A Mitral:", self._crear_linea_parametro(P_PRES_LLEN_E_A, self.ratio_e_a_edit))
        self.e_prima_septal_edit = QLineEdit(); self.e_prima_septal_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.e_prima_septal_edit.setValidator(self.numeric_validator); self.e_prima_septal_edit.setPlaceholderText("cm/s")
        eco_avanzada_form.addRow("e' septal:", self._crear_linea_parametro(P_PRES_LLEN_E_SEPTAL, self.e_prima_septal_edit, "cm/s"))
        self.e_prima_lateral_edit = QLineEdit(); self.e_prima_lateral_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.e_prima_lateral_edit.setValidator(self.numeric_validator); self.e_prima_lateral_edit.setPlaceholderText("cm/s")
        eco_avanzada_form.addRow("e' lateral:", self._crear_linea_parametro(P_PRES_LLEN_E_LATERAL, self.e_prima_lateral_edit, "cm/s"))
        self.e_sobre_e_prima_edit = QLineEdit(); self.e_sobre_e_prima_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.e_sobre_e_prima_edit.setValidator(self.numeric_validator); self.e_sobre_e_prima_edit.setPlaceholderText("ratio") # Para E/e'
        eco_avanzada_form.addRow("Ratio E/e' (promedio):", self._crear_linea_parametro(P_PRES_LLEN_E_E_PRIMA_RATIO, self.e_sobre_e_prima_edit))
        self.vel_it_max_edit = QLineEdit(); self.vel_it_max_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.vel_it_max_edit.setValidator(self.numeric_validator); self.vel_it_max_edit.setPlaceholderText("m/s")
        eco_avanzada_form.addRow("Vel. Máx. Insuf. Tricuspídea:", self._crear_linea_parametro(P_PRES_LLEN_IT_VEL, self.vel_it_max_edit, "m/s"))
        # Derrame Pericárdico con RadioButtons Ausente/Presente
        derr_per_radio_layout = QHBoxLayout(); derr_per_radio_layout.setContentsMargins(0,0,0,0)
        self.derr_per_radio_group = QButtonGroup(self)
        self.derr_per_radio_ausente = QRadioButton("Ausente"); self.derr_per_radio_ausente.setChecked(True)
        self.derr_per_radio_presente = QRadioButton("Presente")
        self.derr_per_radio_group.addButton(self.derr_per_radio_ausente); self.derr_per_radio_group.addButton(self.derr_per_radio_presente)
        derr_per_radio_layout.addWidget(self.derr_per_radio_ausente); derr_per_radio_layout.addWidget(self.derr_per_radio_presente); derr_per_radio_layout.addStretch()
        derr_per_radio_widget = QWidget(); derr_per_radio_widget.setLayout(derr_per_radio_layout)
        eco_avanzada_form.addRow("Derrame Pericárdico:", self._crear_linea_parametro(P_DERR_PERIC_PRESENTE, derr_per_radio_widget, button_group_for_radios=self.derr_per_radio_group))
        self.derr_per_cuantia_edit = QLineEdit(); self.derr_per_cuantia_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.derr_per_cuantia_edit.setValidator(self.numeric_validator); self.derr_per_cuantia_edit.setPlaceholderText("mm")
        eco_avanzada_form.addRow("Cuantía Derr. Pericárdico:", self._crear_linea_parametro(P_DERR_PERIC_CUANTIA, self.derr_per_cuantia_edit, "mm"))
        eco_avanzada_group.setLayout(eco_avanzada_form); content_layout.addWidget(eco_avanzada_group)

        # === Congestión ===
        congestion_group = QGroupBox("Congestión (Pulmonar y Sistémica)"); congestion_form = QFormLayout(); congestion_form.setLabelAlignment(Qt.AlignLeft); congestion_form.setRowWrapPolicy(QFormLayout.WrapLongRows); congestion_form.setSpacing(8)
        # Líneas B con RadioButtons Ausente/Presente
        lineas_b_radio_layout = QHBoxLayout(); lineas_b_radio_layout.setContentsMargins(0,0,0,0)
        self.lineas_b_radio_group = QButtonGroup(self)
        self.lineas_b_radio_ausente = QRadioButton("Ausentes"); self.lineas_b_radio_ausente.setChecked(True)
        self.lineas_b_radio_presente = QRadioButton("Presentes (>3/espacio)")
        self.lineas_b_radio_group.addButton(self.lineas_b_radio_ausente); self.lineas_b_radio_group.addButton(self.lineas_b_radio_presente)
        lineas_b_radio_layout.addWidget(self.lineas_b_radio_ausente); lineas_b_radio_layout.addWidget(self.lineas_b_radio_presente); lineas_b_radio_layout.addStretch()
        lineas_b_radio_widget = QWidget(); lineas_b_radio_widget.setLayout(lineas_b_radio_layout)
        congestion_form.addRow("Líneas B:", self._crear_linea_parametro(P_LINEAS_B_PRESENTE, lineas_b_radio_widget, button_group_for_radios=self.lineas_b_radio_group))
        self.lineas_b_desc_edit = QLineEdit(); self.lineas_b_desc_edit.setPlaceholderText("Localización y hallazgos")
        congestion_form.addRow("Descripción Líneas B:", self._crear_linea_parametro(P_LINEAS_B_DESC, self.lineas_b_desc_edit))
        # Derrame Pleural con RadioButtons Ausente/Presente
        derr_pleural_radio_layout = QHBoxLayout(); derr_pleural_radio_layout.setContentsMargins(0,0,0,0)
        self.derr_pleural_radio_group = QButtonGroup(self)
        self.derr_pleural_radio_ausente = QRadioButton("Ausente"); self.derr_pleural_radio_ausente.setChecked(True)
        self.derr_pleural_radio_presente = QRadioButton("Presente")
        self.derr_pleural_radio_group.addButton(self.derr_pleural_radio_ausente); self.derr_pleural_radio_group.addButton(self.derr_pleural_radio_presente)
        derr_pleural_radio_layout.addWidget(self.derr_pleural_radio_ausente); derr_pleural_radio_layout.addWidget(self.derr_pleural_radio_presente); derr_pleural_radio_layout.addStretch()
        derr_pleural_radio_widget = QWidget(); derr_pleural_radio_widget.setLayout(derr_pleural_radio_layout)
        congestion_form.addRow("Derrame Pleural:", self._crear_linea_parametro(P_DERR_PLEURAL_PRESENTE, derr_pleural_radio_widget, button_group_for_radios=self.derr_pleural_radio_group))
        self.derr_pleural_tipo_combo = QComboBox(); self.derr_pleural_tipo_combo.addItems(["", "Leve", "Moderado", "Severo"])
        congestion_form.addRow("Tipo/Cuantificación:", self._crear_linea_parametro(P_DERR_PLEURAL_TIPO, self.derr_pleural_tipo_combo))
        self.derr_pleural_loc_combo = QComboBox(); self.derr_pleural_loc_combo.addItems(["", "Derecho", "Izquierdo", "Bilateral"])
        congestion_form.addRow("Localización:", self._crear_linea_parametro(P_DERR_PLEURAL_LOC, self.derr_pleural_loc_combo))
        # VCI
        self.vci_diam_edit = QLineEdit(); self.vci_diam_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.vci_diam_edit.setValidator(self.numeric_validator); self.vci_diam_edit.setPlaceholderText("mm")
        congestion_form.addRow("Diámetro Máx. VCI:", self._crear_linea_parametro(P_VCI_DIAM, self.vci_diam_edit, "mm"))
        # VCI Colapso con Radios y campo para mm inspiración
        vci_col_radio_layout = QHBoxLayout(); vci_col_radio_layout.setContentsMargins(0,0,0,0)
        self.vci_colapso_radio_group = QButtonGroup(self)
        self.vci_colapso_radio_mayor = QRadioButton(">50%"); self.vci_colapso_radio_menor = QRadioButton("<50%")
        self.vci_colapso_radio_no_val = QRadioButton("NV Colapso"); self.vci_colapso_radio_no_val.setChecked(True) # Opción para no elegir > o <
        self.vci_colapso_radio_group.addButton(self.vci_colapso_radio_mayor); self.vci_colapso_radio_group.addButton(self.vci_colapso_radio_menor); self.vci_colapso_radio_group.addButton(self.vci_colapso_radio_no_val)
        vci_col_radio_layout.addWidget(self.vci_colapso_radio_mayor); vci_col_radio_layout.addWidget(self.vci_colapso_radio_menor); vci_col_radio_layout.addWidget(self.vci_colapso_radio_no_val); vci_col_radio_layout.addStretch()
        vci_col_radio_widget = QWidget(); vci_col_radio_widget.setLayout(vci_col_radio_layout)
        congestion_form.addRow("Colapso VCI:", self._crear_linea_parametro(P_VCI_COLAPSO_RADIO, vci_col_radio_widget, button_group_for_radios=self.vci_colapso_radio_group))
        self.vci_mm_insp_edit = QLineEdit(); self.vci_mm_insp_edit.setFixedWidth(SHORT_LINE_EDIT_WIDTH); self.vci_mm_insp_edit.setValidator(self.numeric_validator); self.vci_mm_insp_edit.setPlaceholderText("mm insp.")
        congestion_form.addRow("VCI mm Inspiración:", self._crear_linea_parametro(P_VCI_MM_INSPIRACION, self.vci_mm_insp_edit, "mm"))
        # VExUS
        self.vci_dilatada_vexus_check = QCheckBox("VCI > 2cm (para VExUS)")
        congestion_form.addRow("VExUS - VCI dilatada:", self._crear_linea_parametro(P_VEXUS_VCI_DILATADA, self.vci_dilatada_vexus_check))
        self.vsh_patron_combo = QComboBox(); self.vsh_patron_combo.addItems([""] + config.VSH_PATRONES)
        congestion_form.addRow("VExUS - Patrón V. Suprahepática:", self._crear_linea_parametro(P_VEXUS_VSH, self.vsh_patron_combo))
        self.vp_patron_combo = QComboBox(); self.vp_patron_combo.addItems([""] + config.VP_PATRONES)
        congestion_form.addRow("VExUS - Patrón V. Porta:", self._crear_linea_parametro(P_VEXUS_VP, self.vp_patron_combo))
        self.vir_patron_combo = QComboBox(); self.vir_patron_combo.addItems([""] + config.VIR_PATRONES)
        congestion_form.addRow("VExUS - Patrón V. Intrarrenal:", self._crear_linea_parametro(P_VEXUS_VIR, self.vir_patron_combo))
        congestion_group.setLayout(congestion_form); content_layout.addWidget(congestion_group)

        content_layout.addStretch(1)
        self.scroll_content_widget.setLayout(content_layout)
        scroll_area.setWidget(self.scroll_content_widget)
        main_tab_layout.addWidget(scroll_area, 2)
        self.vexus_image_label = QLabel()
        image_path = os.path.join(config.RESOURCES_DIR, "vexus_patterns.png")
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull(): self.vexus_image_label.setPixmap(pixmap.scaledToWidth(DatosEcoTab.TARGET_IMAGE_WIDTH, Qt.SmoothTransformation))
            else: self.vexus_image_label.setText("Error al cargar imagen VExUS."); log_message(f"Pixmap VExUS nulo: {image_path}", "error")
        else: self.vexus_image_label.setText(f"Imagen VExUS no encontrada:\n{image_path}"); log_message(f"Imagen VExUS no encontrada: {image_path}", "warning")
        self.vexus_image_label.setAlignment(Qt.AlignCenter | Qt.AlignTop); self.vexus_image_label.setMinimumWidth(DatosEcoTab.TARGET_IMAGE_WIDTH + 20)
        main_tab_layout.addWidget(self.vexus_image_label, 1)
        self.setLayout(main_tab_layout)

        # Conectar señales de los RadioButton groups que actúan como "Presente/Ausente"
        self.derr_per_radio_group.buttonClicked.connect(partial(self._on_sub_checkbox_changed, self.derr_per_radio_group, P_DERR_PERIC_CUANTIA, [self.derr_per_cuantia_edit]))
        self.lineas_b_radio_group.buttonClicked.connect(partial(self._on_sub_checkbox_changed, self.lineas_b_radio_group, P_LINEAS_B_DESC, [self.lineas_b_desc_edit]))
        self.derr_pleural_radio_group.buttonClicked.connect(partial(self._on_sub_checkbox_changed, self.derr_pleural_radio_group, P_DERR_PLEURAL_TIPO, [self.derr_pleural_tipo_combo, self.derr_pleural_loc_combo]))
    
    # (MÉTODOS cargar_modelo_en_ui y actualizar_modelo COMPLETOS Y ACTUALIZADOS ABAJO)

    def cargar_modelo_en_ui(self):
        for param_key, controls in self.param_controls.items():
            input_widget_or_container = controls["input"]
            nv_check = controls["nv_check"]
            button_group = controls.get("button_group")

            es_no_valorado = self.modelo_informe.param_no_valorado_flags.get(param_key, False)
            nv_check.setChecked(es_no_valorado)
            
            # Habilitar/Deshabilitar el widget de entrada o los componentes del contenedor
            if button_group: # Para QButtonGroups (FEVI cualitativa, Derrame presente/ausente, etc.)
                for rb_in_group in button_group.buttons():
                    rb_in_group.setEnabled(not es_no_valorado)
            else: # Para QLineEdit, QComboBox, QCheckBox individuales
                input_widget_or_container.setEnabled(not es_no_valorado)
            
            if es_no_valorado: # Si es NV, limpiar/resetear
                if isinstance(input_widget_or_container, QLineEdit): input_widget_or_container.clear()
                elif isinstance(input_widget_or_container, QComboBox): input_widget_or_container.setCurrentIndex(0)
                elif isinstance(input_widget_or_container, QCheckBox) and input_widget_or_container != nv_check : input_widget_or_container.setChecked(False)
                elif button_group: # FEVI, Derrame presente/ausente, etc.
                    if param_key == P_FEVI_CUALITATIVA: self.fevi_radio_ninguna.setChecked(True)
                    elif param_key in [P_DERR_PERIC_PRESENTE, P_LINEAS_B_PRESENTE, P_DERR_PLEURAL_PRESENTE]:
                         # Asumir que el primer radio es "Ausente" o "No Estimar"
                         button_group.buttons()[0].setChecked(True)
                    elif param_key == P_VCI_COLAPSO_RADIO:
                        self.vci_colapso_radio_no_val.setChecked(True)
                continue 

            # Cargar valor del modelo si NO es NV
            if param_key == P_VI_SEPTO: input_widget_or_container.setText(str(self.modelo_informe.medidas_vi.septo_iv_mm or ""))
            elif param_key == P_VI_PARED_POST: input_widget_or_container.setText(str(self.modelo_informe.medidas_vi.pared_posterior_vi_mm or ""))
            elif param_key == P_VI_DTDVI: input_widget_or_container.setText(str(self.modelo_informe.medidas_vi.dtdvi_mm or ""))
            elif param_key == P_FEVI_CUALITATIVA:
                fevi_cual_val = self.modelo_informe.medidas_vi.fevi_cualitativa
                found = False
                for rb in button_group.buttons():
                    if rb.text() == fevi_cual_val: rb.setChecked(True); found=True; break
                if not found: self.fevi_radio_ninguna.setChecked(True)
            elif param_key == P_FEVI_PORCENTAJE: input_widget_or_container.setText(str(self.modelo_informe.medidas_vi.fevi_porcentaje or ""))
            elif param_key == P_AI_VOL_IDX: input_widget_or_container.setText(str(self.modelo_informe.medidas_auriculas.ai_vol_ml_m2 or ""))
            elif param_key == P_VD_DIAM_BASAL: input_widget_or_container.setText(str(self.modelo_informe.medidas_vd.vd_diametro_basal_mm or ""))
            elif param_key == P_VD_TAPSE: input_widget_or_container.setText(str(self.modelo_informe.medidas_vd.tapse_mm or ""))
            elif param_key == P_VALV_EST_AO: input_widget_or_container.setChecked(self.modelo_informe.valvulopatias.estenosis_aortica_sig)
            elif param_key == P_VALV_INS_AO: input_widget_or_container.setChecked(self.modelo_informe.valvulopatias.insuficiencia_aortica_sig)
            elif param_key == P_VALV_INS_MI: input_widget_or_container.setChecked(self.modelo_informe.valvulopatias.insuficiencia_mitral_sig)
            elif param_key == P_VALV_INS_TR: input_widget_or_container.setChecked(self.modelo_informe.valvulopatias.insuficiencia_tricuspidea_sig)
            elif param_key == P_PRES_LLEN_E_A: input_widget_or_container.setText(str(self.modelo_informe.presiones_llenado.mitral_e_a_ratio or ""))
            elif param_key == P_PRES_LLEN_E_SEPTAL: input_widget_or_container.setText(str(self.modelo_informe.presiones_llenado.e_prima_septal_cms or ""))
            elif param_key == P_PRES_LLEN_E_LATERAL: input_widget_or_container.setText(str(self.modelo_informe.presiones_llenado.e_prima_lateral_cms or ""))
            elif param_key == P_PRES_LLEN_E_E_PRIMA_RATIO: input_widget_or_container.setText(str(self.modelo_informe.presiones_llenado.e_sobre_e_prima_ratio or ""))
            elif param_key == P_PRES_LLEN_IT_VEL: input_widget_or_container.setText(str(self.modelo_informe.presiones_llenado.it_velocidad_max_ms or ""))
            elif param_key == P_DERR_PERIC_PRESENTE:
                if self.modelo_informe.derrame_pericardico.presente: self.derr_per_radio_presente.setChecked(True)
                else: self.derr_per_radio_ausente.setChecked(True)
                self._on_sub_checkbox_changed(self.derr_per_radio_group, P_DERR_PERIC_CUANTIA, [self.derr_per_cuantia_edit])
            elif param_key == P_DERR_PERIC_CUANTIA: input_widget_or_container.setText(str(self.modelo_informe.derrame_pericardico.cuantia_mm or ""))
            elif param_key == P_LINEAS_B_PRESENTE:
                if self.modelo_informe.lineas_b.presentes: self.lineas_b_radio_presente.setChecked(True)
                else: self.lineas_b_radio_ausente.setChecked(True)
                self._on_sub_checkbox_changed(self.lineas_b_radio_group, P_LINEAS_B_DESC, [self.lineas_b_desc_edit])
            elif param_key == P_LINEAS_B_DESC: input_widget_or_container.setText(self.modelo_informe.lineas_b.descripcion_hallazgos or "")
            elif param_key == P_DERR_PLEURAL_PRESENTE:
                if self.modelo_informe.derrame_pleural.presente: self.derr_pleural_radio_presente.setChecked(True)
                else: self.derr_pleural_radio_ausente.setChecked(True)
                self._on_sub_checkbox_changed(self.derr_pleural_radio_group, P_DERR_PLEURAL_TIPO, [self.derr_pleural_tipo_combo, self.derr_pleural_loc_combo])
            elif param_key == P_DERR_PLEURAL_TIPO: input_widget_or_container.setCurrentText(self.modelo_informe.derrame_pleural.tipo_cuantificacion or "")
            elif param_key == P_DERR_PLEURAL_LOC: input_widget_or_container.setCurrentText(self.modelo_informe.derrame_pleural.localizacion or "")
            elif param_key == P_VCI_DIAM: input_widget_or_container.setText(str(self.modelo_informe.vci.diametro_max_mm or ""))
            elif param_key == P_VCI_COLAPSO_RADIO:
                if self.modelo_informe.vci.colapso_mayor_50 is True: self.vci_colapso_radio_mayor.setChecked(True)
                elif self.modelo_informe.vci.colapso_mayor_50 is False: self.vci_colapso_radio_menor.setChecked(True)
                else: self.vci_colapso_radio_no_val.setChecked(True)
            elif param_key == P_VCI_MM_INSPIRACION: input_widget_or_container.setText(str(self.modelo_informe.vci.mm_inspiracion or ""))
            elif param_key == P_VEXUS_VCI_DILATADA: input_widget_or_container.setChecked(self.modelo_informe.vexus.vci_patologica_vexus)
            elif param_key == P_VEXUS_VSH: input_widget_or_container.setCurrentText(self.modelo_informe.vexus.patron_vena_suprahepatica or "")
            elif param_key == P_VEXUS_VP: input_widget_or_container.setCurrentText(self.modelo_informe.vexus.patron_vena_porta or "")
            elif param_key == P_VEXUS_VIR: input_widget_or_container.setCurrentText(self.modelo_informe.vexus.patron_vena_intrarrenal or "")
        log_message("Modelo cargado en UI de DatosEcoTab.", "debug")


    def actualizar_modelo(self):
        flags = self.modelo_informe.param_no_valorado_flags
        for param_key, controls in self.param_controls.items():
            is_nv = controls["nv_check"].isChecked()
            flags[param_key] = is_nv
            input_widget_or_container = controls["input"]
            button_group = controls.get("button_group")

            if is_nv:
                # VI
                if param_key == P_VI_SEPTO: self.modelo_informe.medidas_vi.septo_iv_mm = None
                elif param_key == P_VI_PARED_POST: self.modelo_informe.medidas_vi.pared_posterior_vi_mm = None
                elif param_key == P_VI_DTDVI: self.modelo_informe.medidas_vi.dtdvi_mm = None
                elif param_key == P_FEVI_CUALITATIVA: self.modelo_informe.medidas_vi.fevi_cualitativa = None
                elif param_key == P_FEVI_PORCENTAJE: self.modelo_informe.medidas_vi.fevi_porcentaje = None
                elif param_key == P_AI_VOL_IDX: self.modelo_informe.medidas_auriculas.ai_vol_ml_m2 = None
                elif param_key == P_VD_DIAM_BASAL: self.modelo_informe.medidas_vd.vd_diametro_basal_mm = None
                elif param_key == P_VD_TAPSE: self.modelo_informe.medidas_vd.tapse_mm = None
                # Valvulopatías
                elif param_key == P_VALV_EST_AO: self.modelo_informe.valvulopatias.estenosis_aortica_sig = False
                elif param_key == P_VALV_INS_AO: self.modelo_informe.valvulopatias.insuficiencia_aortica_sig = False
                elif param_key == P_VALV_INS_MI: self.modelo_informe.valvulopatias.insuficiencia_mitral_sig = False
                elif param_key == P_VALV_INS_TR: self.modelo_informe.valvulopatias.insuficiencia_tricuspidea_sig = False
                # Presiones Llenado
                elif param_key == P_PRES_LLEN_E_A: self.modelo_informe.presiones_llenado.mitral_e_a_ratio = None
                elif param_key == P_PRES_LLEN_E_SEPTAL: self.modelo_informe.presiones_llenado.e_prima_septal_cms = None
                elif param_key == P_PRES_LLEN_E_LATERAL: self.modelo_informe.presiones_llenado.e_prima_lateral_cms = None
                elif param_key == P_PRES_LLEN_E_E_PRIMA_RATIO: self.modelo_informe.presiones_llenado.e_sobre_e_prima_ratio = None
                elif param_key == P_PRES_LLEN_IT_VEL: self.modelo_informe.presiones_llenado.it_velocidad_max_ms = None
                # Derrame Pericárdico
                elif param_key == P_DERR_PERIC_PRESENTE: self.modelo_informe.derrame_pericardico.presente = False # o None si tu modelo lo permite
                elif param_key == P_DERR_PERIC_CUANTIA: self.modelo_informe.derrame_pericardico.cuantia_mm = None
                # Líneas B
                elif param_key == P_LINEAS_B_PRESENTE: self.modelo_informe.lineas_b.presentes = False # o None
                elif param_key == P_LINEAS_B_DESC: self.modelo_informe.lineas_b.descripcion_hallazgos = ""
                # Derrame Pleural
                elif param_key == P_DERR_PLEURAL_PRESENTE: self.modelo_informe.derrame_pleural.presente = False # o None
                elif param_key == P_DERR_PLEURAL_TIPO: self.modelo_informe.derrame_pleural.tipo_cuantificacion = None
                elif param_key == P_DERR_PLEURAL_LOC: self.modelo_informe.derrame_pleural.localizacion = None
                # VCI
                elif param_key == P_VCI_DIAM: self.modelo_informe.vci.diametro_max_mm = None
                elif param_key == P_VCI_COLAPSO_RADIO: self.modelo_informe.vci.colapso_mayor_50 = None
                elif param_key == P_VCI_MM_INSPIRACION: self.modelo_informe.vci.mm_inspiracion = None
                # VExUS
                elif param_key == P_VEXUS_VCI_DILATADA: self.modelo_informe.vexus.vci_patologica_vexus = False
                elif param_key == P_VEXUS_VSH: self.modelo_informe.vexus.patron_vena_suprahepatica = None
                elif param_key == P_VEXUS_VP: self.modelo_informe.vexus.patron_vena_porta = None
                elif param_key == P_VEXUS_VIR: self.modelo_informe.vexus.patron_vena_intrarrenal = None
                continue

            # Si NO es NV, guardar el valor del widget
            if param_key == P_VI_SEPTO: self.modelo_informe.medidas_vi.septo_iv_mm = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_VI_PARED_POST: self.modelo_informe.medidas_vi.pared_posterior_vi_mm = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_VI_DTDVI: self.modelo_informe.medidas_vi.dtdvi_mm = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_FEVI_CUALITATIVA:
                selected_rb = button_group.checkedButton() if button_group else None
                self.modelo_informe.medidas_vi.fevi_cualitativa = selected_rb.text() if selected_rb and selected_rb.text() != "No Estimar" else None
            elif param_key == P_FEVI_PORCENTAJE: self.modelo_informe.medidas_vi.fevi_porcentaje = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_AI_VOL_IDX: self.modelo_informe.medidas_auriculas.ai_vol_ml_m2 = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_VD_DIAM_BASAL: self.modelo_informe.medidas_vd.vd_diametro_basal_mm = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_VD_TAPSE: self.modelo_informe.medidas_vd.tapse_mm = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_VALV_EST_AO: self.modelo_informe.valvulopatias.estenosis_aortica_sig = input_widget_or_container.isChecked()
            elif param_key == P_VALV_INS_AO: self.modelo_informe.valvulopatias.insuficiencia_aortica_sig = input_widget_or_container.isChecked()
            elif param_key == P_VALV_INS_MI: self.modelo_informe.valvulopatias.insuficiencia_mitral_sig = input_widget_or_container.isChecked()
            elif param_key == P_VALV_INS_TR: self.modelo_informe.valvulopatias.insuficiencia_tricuspidea_sig = input_widget_or_container.isChecked()
            elif param_key == P_PRES_LLEN_E_A: self.modelo_informe.presiones_llenado.mitral_e_a_ratio = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_PRES_LLEN_E_SEPTAL: self.modelo_informe.presiones_llenado.e_prima_septal_cms = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_PRES_LLEN_E_LATERAL: self.modelo_informe.presiones_llenado.e_prima_lateral_cms = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_PRES_LLEN_E_E_PRIMA_RATIO: self.modelo_informe.presiones_llenado.e_sobre_e_prima_ratio = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_PRES_LLEN_IT_VEL: self.modelo_informe.presiones_llenado.it_velocidad_max_ms = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_DERR_PERIC_PRESENTE:
                self.modelo_informe.derrame_pericardico.presente = self.derr_per_radio_presente.isChecked() if button_group else False
            elif param_key == P_DERR_PERIC_CUANTIA: self.modelo_informe.derrame_pericardico.cuantia_mm = self._safe_text_to_float(input_widget_or_container) if self.modelo_informe.derrame_pericardico.presente else None
            elif param_key == P_LINEAS_B_PRESENTE:
                self.modelo_informe.lineas_b.presentes = self.lineas_b_radio_presente.isChecked() if button_group else False
            elif param_key == P_LINEAS_B_DESC: self.modelo_informe.lineas_b.descripcion_hallazgos = input_widget_or_container.text().strip() if self.modelo_informe.lineas_b.presentes else ""
            elif param_key == P_DERR_PLEURAL_PRESENTE:
                self.modelo_informe.derrame_pleural.presente = self.derr_pleural_radio_presente.isChecked() if button_group else False
            elif param_key == P_DERR_PLEURAL_TIPO: self.modelo_informe.derrame_pleural.tipo_cuantificacion = input_widget_or_container.currentText() if self.modelo_informe.derrame_pleural.presente and input_widget_or_container.currentText() else None
            elif param_key == P_DERR_PLEURAL_LOC: self.modelo_informe.derrame_pleural.localizacion = input_widget_or_container.currentText() if self.modelo_informe.derrame_pleural.presente and input_widget_or_container.currentText() else None
            elif param_key == P_VCI_DIAM: self.modelo_informe.vci.diametro_max_mm = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_VCI_COLAPSO_RADIO:
                if self.vci_colapso_radio_mayor.isChecked(): self.modelo_informe.vci.colapso_mayor_50 = True
                elif self.vci_colapso_radio_menor.isChecked(): self.modelo_informe.vci.colapso_mayor_50 = False
                else: self.modelo_informe.vci.colapso_mayor_50 = None # Si "NV Colapso" está activo
            elif param_key == P_VCI_MM_INSPIRACION: self.modelo_informe.vci.mm_inspiracion = self._safe_text_to_float(input_widget_or_container)
            elif param_key == P_VEXUS_VCI_DILATADA: self.modelo_informe.vexus.vci_patologica_vexus = input_widget_or_container.isChecked()
            elif param_key == P_VEXUS_VSH: self.modelo_informe.vexus.patron_vena_suprahepatica = input_widget_or_container.currentText() if input_widget_or_container.currentText() else None
            elif param_key == P_VEXUS_VP: self.modelo_informe.vexus.patron_vena_porta = input_widget_or_container.currentText() if input_widget_or_container.currentText() else None
            elif param_key == P_VEXUS_VIR: self.modelo_informe.vexus.patron_vena_intrarrenal = input_widget_or_container.currentText() if input_widget_or_container.currentText() else None

        # log_message(f"Modelo DatosEcoTab actualizado desde UI. Param: {param_key}", "debug") # Mover fuera del bucle
        log_message("Modelo DatosEcoTab completamente actualizado desde UI.", "debug")

    def set_modelo(self, nuevo_modelo_informe: InformeEcoCompleto):
        self.modelo_informe = nuevo_modelo_informe
        self.cargar_modelo_en_ui()
        log_message("Modelo general recargado en DatosEcoTab.", "debug")