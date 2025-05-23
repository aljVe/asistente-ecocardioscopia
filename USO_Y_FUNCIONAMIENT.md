# Guía de Uso y Funcionamiento del Asistente de Ecocardioscopia (EcoReport SEMI)

Este documento describe cómo utilizar el Asistente de Ecocardioscopia y explica cómo la entrada de datos afecta la generación del informe final.

## Principios Generales de Entrada de Datos

1.  **Campos Vacíos:** Si un campo numérico o de texto se deja vacío, generalmente se interpretará como "no medido" o "no especificado" para ese parámetro en particular. No aparecerá en el informe narrativo.
2.  **Checkbox "NV" (No Valorado):**
    * Cada parámetro o grupo pequeño de parámetros tiene una casilla "NV" a su izquierda.
    * **Si marcas "NV"**:
        * El campo de entrada asociado se deshabilitará y su contenido se borrará (o se reseteará a un valor por defecto como "No Estimar").
        * En el modelo de datos interno, este parámetro se marcará explícitamente como "No Valorado".
        * En el informe generado, este parámetro se indicará como "no valorado". Por ejemplo, "Septo interventricular no valorado."
    * **Si desmarcas "NV"**:
        * El campo de entrada se habilitará, permitiéndote introducir un valor.
        * Si no introduces ningún valor y el campo queda vacío, se tratará como en el punto 1 (campo vacío).
3.  **Campos Dependientes:**
    * Algunos campos solo se habilitan si se cumple una condición en un campo "padre". Por ejemplo:
        * La "Cuantía del Derrame Pericárdico" solo se habilita si se marca "Presente" en los radios de "Derrame Pericárdico" (y el parámetro "Derrame Pericárdico" no está marcado como "NV").
        * La "Descripción de Líneas B" solo se habilita si se marca "Presentes" en los radios de "Líneas B".
        * Los campos de "Tipo/Cuantificación" y "Localización" del Derrame Pleural solo se habilitan si se marca "Presente" para Derrame Pleural.
    * Si el campo "padre" se marca como "Ausente" o "NV", los campos dependientes se deshabilitarán, se borrarán y no se incluirán en el informe.

## Especificaciones por Sección de Datos

### 1. Eco Básica (VI, AI, VD)

* **Septo IV, Pared Posterior VI, DTDVI:** Si se dejan vacíos o NV, se indicará "no medido" o "no valorado". Si tienen valor, se mostrarán. La HVI se calcula si hay datos.
* **Estimación Visual FEVI (Radios):**
    * "No Estimar": No se incluirá estimación visual en el informe.
    * Otras opciones (Preservada, Ligeramente Dep., Severamente Dep.): Se incluirá la selección.
    * Si el grupo entero está "NV", se indicará como "no valorado".
* **FEVI Cuantitativa (%):** Si vacío o NV, "no valorado". Si tiene valor, se mostrará y se usará para la clasificación de IC FEVI.
* **Volumen AI Indexado:** Si vacío o NV, "no valorado". Si tiene valor, se mostrará.
* **Diámetro Basal VD, TAPSE:** Si vacíos o NV, "no valorado". Si tienen valor, se mostrarán y se indicará si hay dilatación de VD o TAPSE disminuido.

### 2. Eco Avanzada (Valvulopatías, Presiones, Pericardio)

* **Valvulopatías Significativas (Checkboxes EAo, IAo, IM, IT):**
    * Si un checkbox está marcado (y no está "NV"), se mencionará la valvulopatía como significativa.
    * Si está desmarcado (o "NV"), no se mencionará esa valvulopatía específica.
* **Ratio E/A Mitral, e' septal, e' lateral, Ratio E/e' (promedio), Vel. Máx. Insuf. Tricuspídea:**
    * Si vacíos o "NV", se indicarán como "no valorados" en el contexto de la estimación de presiones de llenado.
    * Si tienen valores, se usarán para la estimación de presiones de llenado del VI.
* **Derrame Pericárdico (Radios Ausente/Presente):**
    * Si "Ausente" (o todo el parámetro "NV"), no se mencionará derrame o se dirá que está ausente/no valorado.
    * Si "Presente":
        * Se activará el campo "Cuantía Derr. Pericárdico".
        * Si "Cuantía" tiene valor (y no está "NV"), se clasificará como leve, moderado o severo.
        * Si "Cuantía" está vacía o "NV", se mencionará la presencia sin especificar cuantía.

### 3. Congestión (Pulmonar y Sistémica)

* **Líneas B (Radios Ausentes/Presentes):**
    * Si "Ausentes" (o todo el parámetro "NV"), se indicará ausencia/no valoración.
    * Si "Presentes":
        * Se activará el campo "Descripción Líneas B".
        * El informe mencionará la presencia. Si hay descripción, se añadirá.
* **Derrame Pleural (Radios Ausente/Presente):**
    * Si "Ausente" (o todo el parámetro "NV"), se indicará ausencia/no valoración.
    * Si "Presente":
        * Se activarán los campos "Tipo/Cuantificación" y "Localización".
        * El informe mencionará la presencia y los detalles seleccionados en los combos.
* **VCI (Diámetro Máx., Colapso por Radios, mm Inspiración):**
    * **Diámetro Máx. VCI:** Si vacío o "NV", "no medido" o "no valorado".
    * **Colapso VCI (Radios >50% / <50% / NV Colapso):**
        * La selección se registrará. "NV Colapso" indica que no se pudo determinar esta característica específica.
        * Si el grupo de radios principal está marcado como "NV" (el checkbox "NV" al lado de la etiqueta "Colapso VCI"), entonces toda esta parte se considera no valorada.
    * **VCI mm Inspiración:** Medida del diámetro en inspiración. Si vacío o "NV", "no medido" o "no valorado".
    * El informe intentará describir la VCI con los datos disponibles y sugerir si la PVC está elevada si hay suficientes datos.
* **VExUS:**
    * **VCI > 2cm (para VExUS) (Checkbox):** Indica si la VCI cumple el criterio de tamaño para VExUS.
    * **Patrones (V. Suprahepática, V. Porta, V. Intrarrenal - ComboBoxes):** Permiten seleccionar el patrón observado.
    * Si los campos relevantes (o sus flags "NV") impiden el cálculo, el informe indicará que el score VExUS no se calculó o que los datos son insuficientes. Si se puede calcular, se mostrará el grado.

## Generación del Informe

* La pestaña "Informe y Acciones" permite introducir metadatos (Realizado por, Comentarios Adicionales) y previsualizar el informe.
* El botón **"Generar/Actualizar Previsualización"** toma todos los datos introducidos en la pestaña "Datos Ecocardiográficos" y los metadatos, y genera el texto narrativo.
* **Omisión de Secciones/Frases:** Si todos los parámetros relevantes para una frase o sección del informe están vacíos o marcados como "NV" (y no tienen una forma específica de reportar "no valorado"), esa frase o sección podría omitirse para mantener el informe conciso y centrado en los hallazgos disponibles.
* **"Comentarios Adicionales / Conclusión":** Este campo de texto libre siempre se incluirá al final del informe si contiene texto.

## Advertencias Importantes

*Recuerda que esta es una herramienta de asistencia. Todos los informes generados deben ser revisados y validados por un profesional médico cualificado. Este software no es un producto sanitario certificado.* (Puedes expandir esto o referenciar la sección completa del `README.md`).