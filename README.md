# TD_Generador-de-reporte-de-operadores

TouchDesigner Report Generator for AI.
Un script en Python para TouchDesigner diseñado para generar reportes en texto plano de tus operadores y pegarlos directamente en herramientas de Inteligencia Artificial (ChatGPT, Claude, Gemini, etc.).
Sirve para darle contexto inmediato a la IA sobre qué tenés seleccionado en tu red, cómo están conectados los operadores, si hay errores activos y cuál es el impacto de rendimiento de ese bloque.

Testeado en TouchDesigner 2025 en Windows

Diseñado por @full_toe.

¿Para qué sirve?
Cuando le pedís ayuda a una IA para resolver un problema en TouchDesigner, explicarle la red manualmente lleva mucho tiempo. Este script automatiza ese proceso:
Da contexto rápido: Captura la estructura de los nodos que selecciones, sus conexiones, entradas, salidas y parámetros modificados.
Diagnostica errores: Extrae los errores y advertencias activas en tus nodos para que la IA sepa exactamente qué está fallando.
Detecta cuellos de botella: Incluye los FPS actuales del proyecto y el tiempo de cook individual de cada nodo.

¿Cómo se usa?
Copiar el script: Copiá el código del script o descargá el archivo del repositorio.
Llevarlo a TouchDesigner: Arrastrá el archivo dentro de tu Network Editor para crear un Text DAT.
Seleccionar los nodos: En tu red, marcá con el mouse los nodos sobre los cuales querés hacer la consulta.
Ejecutar: Hacé clic derecho sobre el Text DAT (sin seleccionarlo) y elegí Run Script.
Copiar y consultar: Se abrirá una ventana emergente con el reporte listo.

En desarrollo:
- Lectura interna de operadores dentro de bases.

⚠️ Aviso de Privacidad
El script analiza el contenido de los operadores seleccionados. Si seleccionas operadores DAT que contengan contraseñas, claves de API o datos sensibles, figurarán en el texto. Revisá todo reporte antes de compartirlo con otros usuarios o la propia IA.
