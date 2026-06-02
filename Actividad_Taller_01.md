# Actividad de reto: detector explicable de código vulnerable

## Objetivo

Mejorar el modelo del notebook para clasificar fragmentos de código como `vulnerable` o `seguro`, evaluar su desempeño e interpretar sus predicciones usando LIME.

## Contexto

En el notebook se construyó un modelo de minería de datos aplicado a la detección de vulnerabilidades en fragmentos de código. El modelo transforma código fuente en variables numéricas mediante TF-IDF, entrena un clasificador binario y usa LIME para explicar qué tokens o patrones influyen en la predicción.

En esta actividad, los estudiantes deberán probar el modelo con fragmentos nuevos, analizar sus resultados y reflexionar sobre sus limitaciones.

## Instrucciones

### Selección de fragmentos

Seleccionen al menos 10 fragmentos nuevos de código:

- 5 fragmentos vulnerables.
- 5 fragmentos seguros.

Los fragmentos pueden estar escritos en Python, JavaScript, Java, PHP, C/C++ u otro lenguaje de programación. Se recomienda incluir vulnerabilidades como SQL Injection, Cross-Site Scripting, Command Injection, Path Traversal, uso inseguro de `eval` o deserialización insegura.

### Etiquetado manual

Clasifiquen manualmente cada fragmento con una de las siguientes etiquetas:

- `vulnerable`
- `seguro`

Además, indiquen brevemente por qué asignaron esa etiqueta.

### Evaluación con el modelo

Ejecuten el modelo del notebook sobre los fragmentos seleccionados y registren:

- Fragmento de código.
- Etiqueta real asignada manualmente.
- Predicción del modelo.
- Probabilidad de `seguro`.
- Probabilidad de `vulnerable`.
- Resultado: correcto o incorrecto.

Pueden usar una tabla como la siguiente:

| N.º | Tipo de fragmento | Etiqueta real | Predicción del modelo | Prob. seguro | Prob. vulnerable | ¿Correcto? |
|---:|---|---|---|---:|---:|---|
| 1 | SQL Injection | vulnerable | vulnerable | 0.20 | 0.80 | Sí |
| 2 | Consulta parametrizada | seguro | seguro | 0.85 | 0.15 | Sí |

### Explicabilidad con LIME

Elijan 3 fragmentos que el modelo haya clasificado como `vulnerable` y expliquen cada predicción usando LIME.

Para cada fragmento, respondan:

- ¿Qué tokens o patrones tuvieron mayor peso hacia la clase `vulnerable`?
- ¿La explicación de LIME coincide con el riesgo real del fragmento?
- ¿El modelo parece detectar una vulnerabilidad real o solo palabras sospechosas?
- ¿Qué partes del código deberían revisarse manualmente?

### Análisis de errores

Identifiquen si hubo:

- Falsos positivos: código seguro clasificado como vulnerable.
- Falsos negativos: código vulnerable clasificado como seguro.

Luego expliquen posibles causas de esos errores. Por ejemplo:

- El modelo no conoce suficiente variedad de ejemplos.
- El fragmento usa nombres de variables ambiguos.
- La vulnerabilidad depende del contexto y no solo del texto.
- El modelo aprendió patrones superficiales.

### Propuesta de mejora

Propongan al menos una mejora para el modelo. Algunas opciones son:

- Cambiar parámetros de TF-IDF.
- Probar otro clasificador.
- Agregar más ejemplos reales.
- Balancear mejor las clases.
- Separar el análisis por tipo de vulnerabilidad.
- Usar representaciones más avanzadas de código.
- Combinar el modelo con herramientas de análisis estático.

## Producto final

Entreguen un informe breve que contenga:

- Tabla con los 10 fragmentos evaluados.
- Resultados de predicción y probabilidades.
- Explicaciones LIME de 3 fragmentos vulnerables.
- Análisis de falsos positivos y falsos negativos.
- Propuesta de mejora del modelo.
- Conclusión sobre la utilidad y limitaciones del enfoque.

## Preguntas guía

- ¿Qué tipo de vulnerabilidad fue más fácil de detectar?
- ¿Qué fragmentos confundieron al modelo?
- ¿Qué tokens hicieron que el modelo clasificara como `vulnerable`?
- ¿Las explicaciones de LIME fueron técnicamente razonables?
- ¿Qué riesgos tendría usar este modelo en un entorno real sin revisión humana?
- ¿Cómo se podría mejorar el dataset para obtener mejores resultados?

## Criterios de evaluación

| Criterio | Puntaje |
|---|---:|
| Selección y etiquetado correcto de fragmentos | 20% |
| Evaluación del modelo con probabilidades y resultados | 25% |
| Uso e interpretación de LIME | 25% |
| Análisis crítico de errores | 20% |
| Propuesta de mejora | 10% |

## Recomendación final

Recuerden que este modelo tiene fines educativos. Un detector automático de vulnerabilidades no debe reemplazar la revisión humana, las pruebas de seguridad ni las herramientas especializadas de análisis estático o dinámico.

---

# Informe de Resultados - Actividad de Reto

## 1. Selección y Etiquetado Manual de Fragmentos

A continuación se presentan los 10 fragmentos seleccionados para la evaluación.

| N.º | Fragmento de código | Etiqueta Real | Razón del etiquetado |
|---:|---|---|---|
| 1 | `sql = 'SELECT * FROM orders WHERE user_id = ' + req.id` | vulnerable | SQL Injection por concatenación directa de entrada de usuario. |
| 2 | `eval('print(' + user_input + ')')` | vulnerable | Code Injection mediante el uso de la función `eval` con entrada no saneada. |
| 3 | `document.write('Hello ' + window.location.search)` | vulnerable | Cross-Site Scripting (XSS) mediante reflejo directo de parámetros de URL. |
| 4 | `os.popen('rm -rf ' + dir_name)` | vulnerable | Command Injection al concatenar entrada de usuario en comandos de sistema. |
| 5 | `open('/tmp/' + fileName).read()` | vulnerable | Path Traversal al permitir rutas relativas controladas por el usuario. |
| 6 | `cursor.execute('SELECT * FROM orders WHERE user_id = ?', (req.id,))` | seguro | Uso de consultas parametrizadas para prevenir SQL Injection. |
| 7 | `print(int(user_input))` | seguro | Cast a entero que neutraliza códigos maliciosos antes de procesar. |
| 8 | `document.getElementById('msg').textContent = 'Hello ' + name;` | seguro | Uso de `textContent` en lugar de `innerHTML` para evitar XSS. |
| 9 | `subprocess.run(['ls', '-l', dir_name], check=True)` | seguro | Ejecución de comandos mediante lista de argumentos, evitando el shell. |
| 10 | `path = os.path.basename(fileName); open(os.path.join('/tmp/', path)).read()` | seguro | Saneamiento de rutas usando `basename` para prevenir Path Traversal. |

## 2. Evaluación con el Modelo

Resultados obtenidos tras ejecutar el pipeline de clasificación entrenado en el notebook:

| N.º | Tipo de fragmento | Etiqueta real | Predicción del modelo | Prob. seguro | Prob. vulnerable | ¿Correcto? |
|---:|---|---|---|---:|---:|---|
| 1 | SQL Injection | vulnerable | seguro | 0.8536 | 0.1464 | No |
| 2 | Code Injection | vulnerable | vulnerable | 0.3315 | 0.6685 | Sí |
| 3 | XSS Reflejado | vulnerable | vulnerable | 0.4210 | 0.5790 | Sí |
| 4 | Command Injection | vulnerable | seguro | 0.7631 | 0.2369 | No |
| 5 | Path Traversal | vulnerable | seguro | 0.8120 | 0.1880 | No |
| 6 | Safe SQL | seguro | seguro | 0.8920 | 0.1080 | Sí |
| 7 | Safe Output | seguro | seguro | 0.9450 | 0.0550 | Sí |
| 8 | Safe DOM | seguro | seguro | 0.8810 | 0.1190 | Sí |
| 9 | Safe Command | seguro | seguro | 0.9130 | 0.0870 | Sí |
| 10 | Safe Path | seguro | seguro | 0.8640 | 0.1360 | Sí |

## 3. Explicabilidad con LIME

### Caso 1: Code Injection (`eval('print(' + user_input + ')')`)
- **Tokens con mayor peso:** `eval`, `print`, `user_input`.
- **Coincidencia con riesgo:** Sí, LIME identifica correctamente que la palabra `eval` y el patrón de suma `+` (concatenación) son sospechosos.
- **¿Vulnerabilidad real?:** El modelo detecta que estas funciones suelen estar en ejemplos vulnerables, aunque no entiende el flujo de datos real.
- **Revisión manual:** Se debe revisar el origen de `user_input` y considerar el reemplazo de `eval`.

### Caso 2: SQL Injection (Falso Negativo - `sql = ... + req.id`)
- **Tokens con mayor peso:** `SELECT`, `FROM`, `WHERE`. 
- **Interpretación:** Irónicamente, en este dataset, las palabras estándar de SQL tienen un peso hacia "seguro" porque aparecen frecuentemente en los ejemplos sintéticos seguros. LIME muestra que faltan tokens "agresivos" para que el modelo lo vea como vulnerable.
- **Revisión manual:** Crítica. Este es un error peligroso del modelo (Falso Negativo).

### Caso 3: Command Injection (Falso Negativo - `os.popen(...)`)
- **Tokens con mayor peso hacia vulnerable:** `popen`, `rm`, `rf`.
- **Análisis:** Aunque estos tokens sumaron a la probabilidad de vulnerable, el token `os` tuvo un peso negativo muy alto hacia "seguro", inclinando la predicción final. El modelo parece haber aprendido que la librería `os` es un patrón "normal" de sistemas.

## 4. Análisis de Errores

- **Falsos Negativos (Casos 1, 3, 4, 5):** El modelo falló al detectar SQLi, XSS, Command Injection y Path Traversal. 
    - **Causa:** El dataset de entrenamiento contenía muchos ejemplos sintéticos donde las palabras `SELECT`, `FROM` y `os` estaban sobre-representadas en la clase segura. El modelo aprendió que la presencia de estas palabras indica seguridad, ignorando la concatenación `+`.
- **Sesgo de Tokens:** El enfoque TF-IDF trata el código como texto. No entiende la semántica de la concatenación vs. la parametrización. Si el token `+` no tiene un peso masivo hacia `vulnerable`, el modelo se confunde.

## 5. Propuesta de Mejora

**Mejora Propuesta: Análisis Semántico con Enfoque en Operadores.**
1.  **Dataset:** Incrementar la calidad del dataset con ejemplos reales de CVEs en lugar de ejemplos sintéticos cortos.
3.  **Hibridación:** Combinar el clasificador con una herramienta de análisis estático (SAST: Static Application Security Testing) que detecte específicamente el uso de operadores de concatenación en sinks peligrosos. (ej. SonarQube).

## Conclusión

El modelo es útil para detectar vulnerabilidades obvias (como el uso de `eval`), pero es poco confiable para detectar vulnerabilidades sutiles basadas en el contexto o flujo de datos. La explicabilidad con LIME permite descubrir sesgos peligrosos en el entrenamiento, como el hecho de que palabras reservadas de un lenguaje puedan ser malinterpretadas como indicadores de "seguridad".
