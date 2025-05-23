# EcoReport SEMI - Asistente de Ecocardioscopia Clínica

Este programa es un asistente diseñado para facilitar la generación de informes de ecocardioscopia clínica a pie de cama, basado en los parámetros y guías de la Sociedad Española de Medicina Interna (SEMI).

## Descripción

El objetivo principal es agilizar el proceso de documentación post-ecocardioscopia, permitiendo al personal médico introducir los hallazgos de manera estructurada y generar un informe narrativo coherente.

## Advertencias Importantes y Limitaciones de Uso

* **Herramienta de Asistencia:** Este software está diseñado como una **herramienta de asistencia** para profesionales médicos cualificados en la generación de borradores de informes ecocardiográficos. **No es una herramienta de diagnóstico.**
* **Supervisión Profesional Obligatoria:** Cualquier informe o dato generado por esta aplicación **debe ser revisado, verificado y validado íntegramente por un profesional médico competente y cualificado** antes de ser utilizado para cualquier propósito clínico, incluyendo diagnóstico, toma de decisiones terapéuticas o cualquier otro fin médico. El profesional es el único responsable del informe final y de las decisiones clínicas.
* **No Reemplaza el Juicio Clínico:** Esta aplicación no reemplaza, ni pretende reemplazar, el conocimiento, la experiencia, la habilidad y el juicio clínico de los profesionales de la salud.
* **No es un Producto Sanitario:** Este software **NO es un producto sanitario certificado** y no ha sido sometido a evaluación por ninguna autoridad regulatoria para tal fin. No debe ser considerado como tal ni utilizado en situaciones donde se requiera un producto sanitario certificado.
* **Uso Bajo Responsabilidad del Usuario:** El software se proporciona "tal cual" ("as is"), sin garantías de ningún tipo, expresas o implícitas. El uso de esta aplicación es enteramente bajo la responsabilidad del usuario. Los desarrolladores no se hacen responsables de errores, omisiones, o cualquier consecuencia derivada del uso de esta herramienta.
* **Propósito Educativo/Asistencial No Crítico:** Considere esta herramienta principalmente para fines de ayuda en la redacción o para uso en entornos donde la supervisión y validación final por un profesional es absoluta y garantizada.


## Características Principales (Versión Actual)

* Interfaz gráfica de usuario intuitiva para la entrada de datos ecocardiográficos.
* Campos de datos basados en el infograma "Ecocardiografía en Insuficiencia Cardíaca" de la SEMI.
* Opciones para marcar parámetros individuales como "No Valorado".
* Generación automática de un informe en formato de texto narrativo (los campos vacíos se omiten).
* Previsualización del informe dentro de la aplicación.
* Opción para copiar el informe generado al portapapeles.
* Exportación del informe a archivo de texto.
* Inclusión de imagen de referencia para patrones VExUS.
* Logging de errores y eventos de la aplicación.

## Tecnologías Utilizadas

* Python 3
* PyQt5 para la interfaz gráfica.

## Instalación y Configuración (Desarrollo)

1.  **Clonar el repositorio (si aplica):**
    ```bash
    git clone [https://github.com/TU_USUARIO/asistente-ecocardioscopia.git](https://github.com/TU_USUARIO/asistente-ecocardioscopia.git)
    cd asistente-ecocardioscopia
    ```
2.  **Crear un entorno virtual:**
    (Dentro de la carpeta "Asistente de ecocardioscopia")
    ```bash
    python -m venv .venv
    ```
3.  **Activar el entorno virtual:**
    * Windows (Command Prompt/PowerShell en Terminal de Cursor):
        ```bash
        .venv\Scripts\activate
        ```
    * macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
4.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    (Asegúrate de que tu archivo `requirements.txt` está actualizado con `PyQt5` y `PyInstaller`).

## Uso

1.  Asegúrate de que el entorno virtual esté activado.
2.  Navega a la carpeta raíz del proyecto "Asistente de ecocardioscopia" en el terminal.
3.  Ejecuta la aplicación:
    ```bash
    python ecoreport_semi/main.py
    ```

## Cómo Generar el Ejecutable (`.exe`)

1.  Asegúrate de que el entorno virtual esté activado y `PyInstaller` esté listado en `requirements.txt` e instalado.
2.  Desde la carpeta raíz "Asistente de ecocardioscopia", ejecuta:
    ```bash
    python build.py
    ```
3.  El ejecutable se encontrará en la carpeta `dist/`.

## Autor

* **Alejandro Venegas Robles**
* Contacto: `alejandro2196vr@gmail.com`

*Idea original **Jorge Rubio Gracia**


## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
