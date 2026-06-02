# Actividad de Aprendizaje: Detección de Vulnerabilidades con Minería de Datos

**Curso:** Minería de Datos aplicada a Ciberseguridad
**Docente:** Angel Geovanny Cudco Pomagualli
**Nivel:** Medio (intermedio)
**Duración estimada:** 2 a 3 horas
**Modalidad:** Individual
**Pre-requisitos:** Notebook base ya ejecutado (`Taller_02_OWASP_Top10_Mineria_Datos.ipynb`)

---

## 1. Propósito de la actividad

Consolidar los conceptos vistos en el taller mediante la **manipulación guiada** del notebook base. No se busca construir un modelo desde cero, sino **comprender cómo funciona cada parte** del pipeline (dataset → vectorización → modelo → explicabilidad) y experimentar con pequeños cambios controlados.

> Esta actividad **NO es un reto abierto**. Cada paso tiene una pista y un resultado esperado. Si te quedas más de 30 minutos atascado en un paso, revisa la pista o consulta con un compañero.

---

## 2. Resultados de aprendizaje

Al terminar esta actividad, podrás:

1. Explicar con tus palabras qué hace cada bloque del notebook.
2. Modificar parámetros del modelo y predecir cómo cambiarán las métricas.
3. Interpretar una matriz de confusión multiclase.
4. Leer una gráfica SHAP y una explicación LIME sin ayuda externa.
5. Detectar al menos una limitación del clasificador.

---

## 3. Antes de empezar

1. Abre el notebook `Taller_02_OWASP_Top10_Mineria_Datos.ipynb` en Jupyter o Google Colab.
2. Ejecuta todas las celdas en orden (Cell → Run All). Verifica que no haya errores.
3. Confirma que tienes instalado: `scikit-learn`, `pandas`, `matplotlib`, `seaborn`, `shap`, `lime`.
4. Crea un archivo nuevo llamado `respuestas_<tu_apellido>.md` donde irás respondiendo las preguntas.

---

## 4. Parte A — Exploración del dataset

### Tarea A.1 — Inspeccionar la distribución

En la sección **3 (Construcción del dataset)** del notebook:

1. Agrega una celda nueva al final de esa sección y ejecuta:
   ```python
   print(df['etiqueta'].value_counts())
   print('Total de fragmentos:', len(df))
   ```
2. **Responde:**
   - ¿Cuántos fragmentos tiene cada categoría OWASP?
   - ¿El dataset está balanceado o desbalanceado? Justifica.

> **Pista:** Un dataset está balanceado si todas las clases tienen aproximadamente la misma cantidad de muestras (diferencia < 10%).

### Tarea A.2 — Cambiar el tamaño del dataset

En la celda donde se llama `generar_dataset(PLANTILLAS, n_por_clase=80)`:

1. Cambia `n_por_clase=80` por `n_por_clase=30`.
2. **Re-ejecuta** desde esa celda hasta el final del notebook (Cell → Run All Below).
3. **Responde:**
   - ¿Bajó el accuracy del Random Forest? ¿En cuánto?
   - ¿Qué categoría se ve más afectada al reducir los datos? Observa la matriz de confusión.

> **Resultado esperado:** El accuracy debería bajar entre 5 y 15 puntos porcentuales. Algunas categorías con vocabulario menos distintivo (ej. A04 o A09) sufren más.

4. **Restaura** `n_por_clase=80` antes de continuar y vuelve a ejecutar.

---

## 5. Parte B — Preprocesamiento y vectorización

### Tarea B.1 — Entender el tokenizador

Revisa la función `tokenizer_codigo` en la sección 5 del notebook.

1. Ejecuta en una celda nueva:
   ```python
   ejemplo = "cursor.execute(f'SELECT * FROM users WHERE id={user_id}')"
   print(tokenizer_codigo(ejemplo))
   ```
2. **Responde:**
   - ¿Cuántos tokens generó?
   - ¿Por qué crees que separa los símbolos `=`, `*`, `(` de los identificadores?
   - ¿Qué pasaría si solo usáramos `texto.split()` como tokenizador? Pruébalo y comenta.

### Tarea B.2 — Experimentar con n-gramas

En la celda del `TfidfVectorizer`:

1. Cambia `ngram_range=(1, 2)` por `ngram_range=(1, 1)` (solo unigramas).
2. Re-entrena el Random Forest y observa el accuracy.
3. Cambia ahora a `ngram_range=(1, 3)` (hasta trigramas).
4. **Responde en una tabla:**

| ngram_range | Tamaño del vocabulario | Accuracy RF |
|---|---|---|
| (1, 1) | ? | ? |
| (1, 2) | ? | ? |
| (1, 3) | ? | ? |

5. ¿Cuál configuración te parece mejor? Justifica considerando precisión vs. costo computacional.

> **Pista:** El tamaño del vocabulario se obtiene con `len(vectorizer.vocabulary_)`.

---

## 6. Parte C — Modelado

### Tarea C.1 — Modificar el Random Forest

En la celda del Random Forest:

1. Entrena tres versiones cambiando solo `n_estimators`:
   - `n_estimators=10`
   - `n_estimators=100`
   - `n_estimators=300` (valor original)
2. Anota el accuracy de cada uno en tu archivo de respuestas.
3. **Responde:**
   - ¿Mejora indefinidamente el accuracy al aumentar `n_estimators`?
   - ¿En qué punto deja de ser rentable agregar más árboles?

### Tarea C.2 — Probar un modelo nuevo

Agrega una celda nueva después de la del Random Forest y entrena un **Multinomial Naive Bayes** (modelo clásico para clasificación de texto):

```python
from sklearn.naive_bayes import MultinomialNB

nb = MultinomialNB()
nb.fit(X_train_vec, y_train)
y_pred_nb = nb.predict(X_test_vec)

print(f'Accuracy Naive Bayes: {accuracy_score(y_test, y_pred_nb):.4f}')
print(classification_report(y_test, y_pred_nb, zero_division=0))
```

**Responde:**
- ¿Cómo se compara Naive Bayes con Random Forest y Regresión Logística?
- ¿En qué categoría OWASP funciona mejor Naive Bayes y en cuál peor?

---

## 7. Parte D — Interpretación de la matriz de confusión

Observa la matriz de confusión del Random Forest (sección 7 del notebook) y responde:

1. ¿Hay alguna categoría que el modelo confunda sistemáticamente con otra? Anota el par y propón una explicación.
2. ¿Qué significa una celda con valor alto **fuera** de la diagonal principal?
3. Calcula manualmente la precision para la clase `A03_Injection`:
   - **Pista:** precision = TP / (TP + FP) = `cm[A03, A03] / sum(cm[:, A03])`
   - Verifica tu cálculo con el `classification_report`.

---

## 8. Parte E — Explicabilidad SHAP y LIME

### Tarea E.1 — Leer SHAP global

En la sección 8 (SHAP global), revisa el gráfico de los **Top 20 tokens más influyentes**:

1. Anota los **5 tokens más importantes**.
2. **Responde:**
   - ¿Reconoces alguno como típico de una categoría OWASP específica? (ej. `md5` → A02, `pickle` → A08)
   - ¿Aparece algún token "sospechoso" que parezca artefacto del dataset sintético (nombres genéricos, números)?

### Tarea E.2 — Analizar tres predicciones con LIME

Usa la función `analizar_codigo(...)` de la sección 10 del notebook con estos tres fragmentos:

**Fragmento 1 — Vulnerabilidad obvia:**
```python
fragmento_1 = """
def login(username, password):
    query = "SELECT * FROM users WHERE u='" + username + "' AND p='" + password + "'"
    return db.execute(query)
"""
analizar_codigo(fragmento_1)
```

**Fragmento 2 — Vulnerabilidad sutil:**
```python
fragmento_2 = """
token = jwt.encode({'user': username}, key='secret', algorithm='HS256')
"""
analizar_codigo(fragmento_2)
```

**Fragmento 3 — Código aparentemente seguro:**
```python
fragmento_3 = """
import bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
"""
analizar_codigo(fragmento_3)
```

**Responde para cada uno:**

| Fragmento | Categoría predicha | Confianza | ¿Es correcta? | Palabra más influyente en LIME |
|---|---|---|---|---|
| 1 | ? | ? | ? | ? |
| 2 | ? | ? | ? | ? |
| 3 | ? | ? | ? | ? |

**Reflexión adicional (mínimo 100 palabras):** ¿En cuál de los tres casos confías más en la predicción del modelo y por qué? ¿Qué te dice LIME que no te diría solo la probabilidad?

---

## 9. Pregunta integradora final

Responde en máximo media página:

> Imagina que tu universidad quiere integrar este clasificador en su pipeline de revisión de tareas de programación para detectar código inseguro entregado por los estudiantes. **Listar 3 razones por las que NO desplegarías el modelo tal como está**, y para cada razón propón una mejora concreta.

---

## 10. Entrega

Sube a la plataforma del curso:

1. `respuestas_<tu_apellido>.md` (o `.pdf`) con todas las respuestas de las Partes A a E + pregunta integradora.
2. `notebook_modificado.ipynb` con las celdas adicionales que agregaste durante la actividad (ejecutado).

**Tiempo total estimado:** 2 a 3 horas
**Fecha límite:** según indicaciones del docente en aula.

---

## 11. Rúbrica de evaluación

**Nota máxima de la actividad: 20 puntos.**

Cada uno de los 6 criterios se califica **sobre 20 puntos** según su nivel de logro. La nota final es un **promedio ponderado** por porcentajes:

$$ \text{Nota final} = \sum_{i=1}^{6} (\text{nota}_i \times \text{peso}_i) $$

### Pesos por criterio

| # | Criterio | Peso |
|---|---|---|
| 1 | Exploración del dataset (Parte A) | 15 % |
| 2 | Preprocesamiento y vectorización (Parte B) | 15 % |
| 3 | Modelado (Parte C) | 15 % |
| 4 | Matriz de confusión (Parte D) | 15 % |
| 5 | Explicabilidad SHAP y LIME (Parte E) | 25 % |
| 6 | Pregunta integradora | 15 % |
| | **Total** | **100 %** |

### Escala de niveles de logro (aplica a todos los criterios)

| Nivel | Rango de nota (sobre 20) |
|---|---|
| Excelente | 18 – 20 |
| Bueno | 14 – 17 |
| Aceptable | 11 – 13 |
| Insuficiente | 0 – 10 |

### Criterio 1 — Exploración del dataset (Parte A)

| Nivel | Descripción |
|---|---|
| Excelente (18-20) | Identifica correctamente la distribución, justifica el balance con datos, observa con claridad el impacto de reducir `n_por_clase` y nombra la categoría más afectada. |
| Bueno (14-17) | Identifica la distribución y nota el cambio de accuracy, pero la justificación es superficial. |
| Aceptable (11-13) | Responde solo parcialmente o sin justificación numérica. |
| Insuficiente (0-10) | Respuestas incompletas o incorrectas. |

### Criterio 2 — Preprocesamiento y vectorización (Parte B)

| Nivel | Descripción |
|---|---|
| Excelente (18-20) | Explica el tokenizador correctamente, llena la tabla de n-gramas completa y justifica el trade-off precisión vs. costo. |
| Bueno (14-17) | Llena la tabla completa pero la justificación es débil o falta el experimento con `texto.split()`. |
| Aceptable (11-13) | Llena la tabla parcialmente o sin justificación. |
| Insuficiente (0-10) | No completa la tabla ni explica el tokenizador. |

### Criterio 3 — Modelado (Parte C)

| Nivel | Descripción |
|---|---|
| Excelente (18-20) | Compara las 3 configuraciones de Random Forest, entrena correctamente Naive Bayes e interpreta diferencias entre los 3 modelos con argumentos válidos. |
| Bueno (14-17) | Hace los experimentos pero la comparación entre modelos es descriptiva, sin interpretación. |
| Aceptable (11-13) | Solo ejecuta los modelos sin comparar ni interpretar. |
| Insuficiente (0-10) | Modelo no se entrena o no hay análisis. |

### Criterio 4 — Matriz de confusión (Parte D)

| Nivel | Descripción |
|---|---|
| Excelente (18-20) | Identifica un par de clases confundidas, propone una hipótesis razonable y calcula manualmente la precision con el resultado coincidente al `classification_report`. |
| Bueno (14-17) | Calcula precision correctamente pero la interpretación del par confundido es débil. |
| Aceptable (11-13) | Cálculo de precision con error menor o interpretación ausente. |
| Insuficiente (0-10) | Cálculo incorrecto y sin interpretación. |

### Criterio 5 — Explicabilidad SHAP y LIME (Parte E)

| Nivel | Descripción |
|---|---|
| Excelente (18-20) | Identifica los 5 tokens de SHAP, los asocia a categorías OWASP, completa la tabla de los 3 fragmentos y la reflexión final argumenta con criterios técnicos (confianza, dispersión de probabilidades, palabras influyentes). |
| Bueno (14-17) | Tabla completa y reflexión presente pero los argumentos son superficiales o generales. |
| Aceptable (11-13) | Tabla incompleta o reflexión muy breve sin sustento. |
| Insuficiente (0-10) | No completa la tabla ni redacta reflexión. |

### Criterio 6 — Pregunta integradora

| Nivel | Descripción |
|---|---|
| Excelente (18-20) | Propone 3 razones bien fundamentadas (ej. sesgo del dataset, falsos positivos, falta de soporte multilenguaje) con mejoras concretas y aplicables. |
| Bueno (14-17) | Propone 3 razones pero las mejoras son genéricas o solo se desarrollan 2. |
| Aceptable (11-13) | Propone 1-2 razones o las mejoras no responden a las razones planteadas. |
| Insuficiente (0-10) | Respuesta vaga o ausente. |

### Ejemplo de cálculo de nota final

Supongamos que un estudiante obtiene:

| Criterio | Nota /20 | Peso | Aporte |
|---|---|---|---|
| 1 — Parte A | 18 | 15 % | 2.70 |
| 2 — Parte B | 15 | 15 % | 2.25 |
| 3 — Parte C | 16 | 15 % | 2.40 |
| 4 — Parte D | 14 | 15 % | 2.10 |
| 5 — Parte E | 19 | 25 % | 4.75 |
| 6 — Integradora | 17 | 15 % | 2.55 |
| **Nota final** | | | **16.75 / 20** |

### Escala global de la nota final

| Nota final | Calificación cualitativa |
|---|---|
| 18 – 20 | Muy bueno — comprendiste el pipeline completo. |
| 14 – 17 | Bueno — entiendes la mayoría de conceptos, revisa puntos débiles. |
| 11 – 13 | Aceptable — necesitas reforzar interpretación de modelos. |
| 0 – 10 | A reforzar — repasa el notebook base con el docente. |

---

## 12. Recursos de apoyo

- Notebook base: `Taller_OWASP_Top10_Mineria_Datos.ipynb`
- [OWASP Top 10 (2021)](https://owasp.org/Top10/)
- [Documentación de scikit-learn — classification report](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html)
- [SHAP — guía de inicio rápido](https://shap.readthedocs.io/en/latest/example_notebooks/overviews/An%20introduction%20to%20explainable%20AI%20with%20Shapley%20values.html)
- [LIME — tutorial de texto](https://marcotcr.github.io/lime/tutorials/Lime%20-%20basic%20usage%2C%20two%20class%20case.html)

---

## 13. Recomendaciones

- **Lee toda la actividad antes de empezar** para planificar tu tiempo.
- **No copies y pegues respuestas** entre compañeros: cada modificación al notebook genera resultados ligeramente distintos por el `random_state` y se nota.
- **Si una celda demora mucho**, reduce temporalmente `n_estimators` o el tamaño del dataset durante tus experimentos, pero restaura los valores originales antes de entregar.
- **Documenta tus observaciones en celdas Markdown** del notebook — eso facilita la revisión.
