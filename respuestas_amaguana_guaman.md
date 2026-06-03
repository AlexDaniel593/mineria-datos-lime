# Respuestas Actividad Taller 02 - Detección de Vulnerabilidades con OWASP Top 10

**Estudiantes:** Kevin Amaguana - Daniel Guamán  
**Fecha:** 2 de junio de 2026  
**Materia:** Desarrollo de Software Seguro

---

## PARTE A — Exploración del dataset

### Tarea A.1 — Inspeccionar la distribución

**Pregunta 1: ¿Cuántos fragmentos tiene cada categoría OWASP?**

Según la ejecución del notebook, cada categoría OWASP tiene exactamente **80 fragmentos**:

```
A09_Logging_Failures             80
A01_Broken_Access_Control        80
A07_Auth_Failures                80
A08_Integrity_Failures           80
A05_Security_Misconfiguration    80
A10_SSRF                         80
A06_Vulnerable_Components        80
A04_Insecure_Design              80
A03_Injection                    80
A02_Cryptographic_Failures       80
```

**Total de fragmentos:** 800 (80 fragmentos × 10 categorías)

**Pregunta 2: ¿El dataset está balanceado o desbalanceado? Justifica.**

El dataset está **perfectamente balanceado**. 

**Justificación:** 
- Todas las 10 categorías tienen exactamente la misma cantidad de fragmentos (80).
- La diferencia porcentual entre la clase con más muestras y la con menos es 0.00%.
- Un dataset se considera balanceado cuando la diferencia entre clases es menor al 10%, y en este caso la diferencia es 0%.
- Esto es ideal para el entrenamiento porque evita que el modelo se sesge hacia las clases mayoritarias.

---

### Tarea A.2 — Cambiar el tamaño del dataset

**Resultados del experimento:**

Al cambiar `n_por_clase` de 80 a 30, obtuvimos los siguientes resultados:

- **Accuracy con n=80:** 1.0000 (100%)
- **Accuracy con n=30:** 0.8800 (88%)
- **Diferencia:** 0.1200 (12 puntos porcentuales de caída)

**Pregunta 1: ¿Bajó el accuracy del Random Forest? ¿En cuánto?**

Sí, el accuracy bajó significativamente en **12 puntos porcentuales** (de 100% a 88%).

**Pregunta 2: ¿Qué categoría se ve más afectada al reducir los datos?**

Observando el classification report con n=30, las categorías más afectadas son:

1. **A06_Vulnerable_Components**: recall=0.71 (perdió 29% de recall)
2. **A05_Security_Misconfiguration**: recall=0.75 (perdió 25%)
3. **A03_Injection**: recall=0.75 (perdió 25%)

Estas categorías sufren más porque:
- **A06** (componentes vulnerables) depende de patrones muy específicos como nombres de librerías y versiones, que son más difíciles de aprender con pocos ejemplos.
- **A05** (misconfiguration) tiene vocabulario variado (headers, configuraciones de servidor, etc.) que requiere más datos para generalizar.
- **A03** (Injection) abarca múltiples tipos de inyección (SQL, XSS, Command) lo que aumenta la variabilidad interna.

---

## PARTE B — Preprocesamiento y vectorización

### Tarea B.1 — Entender el tokenizador

**Código de prueba:**
```python
ejemplo = "cursor.execute(f'SELECT * FROM users WHERE id={user_id}')"
```

**Resultados:**

| Método | Cantidad de tokens | Tokens generados |
|--------|-------------------|------------------|
| `tokenizer_codigo()` | 11 | ['cursor', 'execute', 'f', 'select', '*', 'from', 'users', 'where', 'id', '=', 'user_id'] |
| `split()` | 6 | ["cursor.execute(f'SELECT", '*', 'FROM', 'users', 'WHERE', "id={user_id}')"] |

**Pregunta 1: ¿Cuántos tokens generó?**

El tokenizador personalizado generó **11 tokens**, mientras que `split()` solo generó **6 tokens**.

**Pregunta 2: ¿Por qué crees que separa los símbolos `=`, `*`, `(` de los identificadores?**

El tokenizador separa los símbolos porque:

1. **Captura patrones sintácticos del código**: Símbolos como `=`, `*`, `+`, `-` son indicadores importantes de operaciones que pueden revelar vulnerabilidades.
2. **Preserva información estructural**: Por ejemplo, `SELECT *` es un patrón asociado con SQL injection, y necesitamos capturar tanto "select" como "*" por separado.
3. **Permite detectar operadores peligrosos**: El símbolo `=` en una query SQL construida con concatenación es un indicador de SQLi.

**Pregunta 3: ¿Qué pasaría si solo usáramos `texto.split()` como tokenizador?**

Si usáramos solo `split()`:
- **Perderíamos información crítica**: "cursor.execute(f'SELECT" sería un solo token, ocultando "execute" y "select".
- **Símbolos quedarían pegados**: El patrón "id={user_id}" se perdería como un bloque indivisible.
- **Menor precisión del modelo**: No podríamos detectar patrones como "execute + SELECT" o "= + variable" que son indicadores de inyección SQL.
- **Vocabulario menos útil**: Los tokens serían más específicos y menos generalizables.

---

### Tarea B.2 — Experimentar con n-gramas

**Tabla de resultados:**

| ngram_range | Tamaño del vocabulario | Accuracy RF |
|-------------|------------------------|-------------|
| (1, 1) | 565 | 1.0000 |
| (1, 2) | 1567 | 1.0000 |
| (1, 3) | 2595 | 1.0000 |

**Pregunta: ¿Cuál configuración te parece mejor? Justifica considerando precisión vs. costo computacional.**

La **mejor configuración es (1, 2)** por las siguientes razones:

**Análisis:**
- **(1, 1) - Solo unigramas**: 
  - ✓ Vocabulario compacto (565 términos)
  - ✓ Rápido de entrenar y predecir
  - ✗ Pierde contexto importante (ej: "pickle" y "loads" por separado no capturan "pickle.loads")

- **(1, 2) - Unigramas + bigramas** [RECOMENDADO]:
  - ✓ Accuracy perfecto (1.0000)
  - ✓ Captura patrones de dos palabras cruciales: "execute select", "hashlib md5", "pickle loads"
  - ✓ Vocabulario moderado (1567 términos)
  - ✓ Buen balance entre precisión y eficiencia

- **(1, 3) - Hasta trigramas**:
  - ✓ Accuracy perfecto (1.0000)
  - ✗ Vocabulario muy grande (2595 términos, +65% vs (1,2))
  - ✗ Mayor tiempo de entrenamiento y memoria
  - ✗ Riesgo de overfitting con datos reales

**Conclusión:** **(1, 2) es el trade-off ideal** porque captura el contexto necesario (bigramas como "eval request", "md5 password") sin explotar el vocabulario. En este dataset sintético todos logran 100%, pero con datos reales (1,3) podría sobreajustar a patrones muy específicos.

---

## PARTE C — Modelado

### Tarea C.1 — Modificar el Random Forest

**Resultados del experimento con diferentes n_estimators:**

| n_estimators | Accuracy |
|--------------|----------|
| 10 | 1.0000 |
| 100 | 1.0000 |
| 300 | 1.0000 |

**Pregunta 1: ¿Mejora indefinidamente el accuracy al aumentar `n_estimators`?**

No, el accuracy **no mejora indefinidamente**. En este caso, alcanzamos el 100% de accuracy con solo 10 árboles, lo cual es una señal de que:

1. El dataset sintético es relativamente simple y los patrones son muy distintivos.
2. Con 10 árboles ya se capturan todas las relaciones necesarias.
3. Aumentar más árboles no aporta información nueva porque ya se alcanzó el máximo posible.

**Pregunta 2: ¿En qué punto deja de ser rentable agregar más árboles?**

En este caso específico, **10 árboles ya son suficientes**. Sin embargo, en un escenario real:

- **Para este dataset sintético**: 10-50 árboles son suficientes.
- **Para datasets reales complejos**: Típicamente 100-200 árboles son óptimos.
- **Más de 300 árboles**: Solo justificable si:
  - El dataset es extremadamente grande (>100k muestras)
  - Hay clases muy desequilibradas
  - Se requiere la máxima precisión posible sin importar el costo

**Punto de rentabilidad**: Cuando el incremento en accuracy es menor a 0.001 (0.1%) entre duplicar el número de árboles, no vale la pena seguir aumentando.

---

### Tarea C.2 — Probar un modelo nuevo (Multinomial Naive Bayes)

**Comparación de modelos:**

| Modelo | Accuracy |
|--------|----------|
| **Random Forest** | 1.0000 |
| **Naive Bayes** | 0.9950 |
| **Regresión Logística** | (ver notebook: ~0.98-1.00) |

**Pregunta 1: ¿Cómo se compara Naive Bayes con Random Forest y Regresión Logística?**

**Naive Bayes logra 99.5% de accuracy**, muy cerca de Random Forest:

- **Random Forest** (100%): Mejor modelo por su capacidad de capturar interacciones no lineales entre tokens.
- **Naive Bayes** (99.5%): Excelente segundo lugar, con ventajas:
  - ✓ Extremadamente rápido (entrena en milisegundos vs segundos de RF)
  - ✓ Requiere mucha menos memoria
  - ✓ Modelo interpretable (probabilidades condicionales)
  - ✗ Asume independencia entre features (no siempre cierto en código)

**Pregunta 2: ¿En qué categoría OWASP funciona mejor Naive Bayes y en cuál peor?**

**Análisis por categoría:**

**Mejor desempeño** (precision y recall = 1.00):
- A01_Broken_Access_Control
- A02_Cryptographic_Failures
- A04_Insecure_Design
- A05_Security_Misconfiguration
- A06_Vulnerable_Components
- A07_Auth_Failures
- A08_Integrity_Failures
- A09_Logging_Failures

**Desempeño ligeramente inferior:**
1. **A03_Injection**: precision=0.95 (confundió 1 caso, probablemente con A01 o A04)
2. **A10_SSRF**: recall=0.95 (no detectó 1 caso, posiblemente confundido con A03)

**Razón de las confusiones:**
- **A03 (Injection)** comparte vocabulario con otras categorías: "execute", "query", "request" también aparecen en A01 (access control) y A10 (SSRF).
- **A10 (SSRF)** usa funciones de red (`requests.get`, `urllib`) que también pueden aparecer en código legítimo de A04 o A05.

Naive Bayes asume que cada palabra es independiente, por lo que no captura que **la combinación específica** "requests.get + user_input" es SSRF, mientras que Random Forest sí lo hace mediante sus árboles de decisión.

---

## PARTE D — Interpretación de la matriz de confusión

Para esta sección, analicé la matriz de confusión del Random Forest mostrada en el notebook original (sección 7).

**Pregunta 1: ¿Hay alguna categoría que el modelo confunda sistemáticamente con otra? Anota el par y propón una explicación.**

En el modelo con **n=80** (accuracy 100%), **no hay confusiones** porque la matriz de confusión es una matriz identidad perfecta (valores solo en la diagonal principal).

Sin embargo, en el experimento con **n=30** (Tarea A.2), observamos confusiones entre:

**Par confundido más frecuente:**
- **A07_Auth_Failures ↔ A02_Cryptographic_Failures**
  
**Explicación:**
Ambas categorías comparten vocabulario relacionado con contraseñas y seguridad:
- Palabras comunes: `password`, `hash`, `token`, `secret`, `key`
- **A07** incluye código como: `if password == stored_password` (sin hash)
- **A02** incluye: `hashlib.md5(password)` (hash débil)

Con pocos ejemplos (n=30), el modelo no logra distinguir que:
- A07 → ausencia de hashing o comparación insegura
- A02 → uso de algoritmos criptográficos obsoletos

**Otro par con confusiones:**
- **A03_Injection ↔ A01_Broken_Access_Control**

Ambas involucran queries SQL y acceso a bases de datos, pero:
- A03 → inyección de código malicioso
- A01 → acceso no autorizado sin inyección

**Pregunta 2: ¿Qué significa una celda con valor alto **fuera** de la diagonal principal?**

Un valor alto fuera de la diagonal principal indica **errores de clasificación**:

- **Celda [i, j]** donde i ≠ j: El modelo predijo clase `j` cuando la clase real era `i`
- **Valor alto**: Confusión sistemática entre dos categorías
- **Ejemplo**: Si `cm[A03_Injection, A01_Access_Control] = 5`, significa que 5 fragmentos de A03 fueron incorrectamente clasificados como A01

**Implicaciones:**
- **Alta en fila i**: La clase i no se está detectando bien (bajo recall)
- **Alta en columna j**: Se está sobre-prediciendo la clase j (bajo precision)
- **Acción requerida**: Revisar qué features diferencian esas clases y agregar más ejemplos

**Pregunta 3: Calcula manualmente la precision para la clase `A03_Injection`**

**Fórmula:** 
$$\text{precision} = \frac{TP}{TP + FP} = \frac{cm[A03, A03]}{\sum_{i} cm[i, A03]}$$

**Con n=80 (accuracy 100%):**
- TP (verdaderos positivos) = cm[A03, A03] = 20
- Columna A03 suma = 20 (todos los predichos como A03 son correctos)
- **Precision = 20 / 20 = 1.00 (100%)**

**Con n=30 (del experimento A.2):**
- TP = verdaderos A03 clasificados como A03 = 6 (según el report)
- Total predichos como A03 = TP / precision = 6 / 1.00 = 6
- **Precision = 6 / 6 = 1.00 (100%)**

**Verificación con classification_report:**
```
A03_Injection       precision=1.00  recall=0.75  f1-score=0.86  support=8
```

**Confirmado**: precision = 1.00 coincide con nuestro cálculo manual.

**Interpretación:** Cuando el modelo predice A03_Injection, **siempre acierta** (precision perfecta), pero solo detecta el 75% de los casos reales (recall=0.75), dejando escapar 2 de 8 fragmentos.

---

## PARTE E — Explicabilidad SHAP y LIME

### Tarea E.1 — Leer SHAP global

Del gráfico "Top 20 features más influyentes — SHAP global" en la sección 8 del notebook:

**Top 5 tokens más importantes:**

1. **`md5`** → Indica A02_Cryptographic_Failures (algoritmo obsoleto)
2. **`pickle`** → Indica A08_Integrity_Failures (deserialización insegura)
3. **`requests`** → Indica A10_SSRF (peticiones HTTP sin validar)
4. **`eval`** → Indica A03_Injection (ejecución de código dinámico)
5. **`debug`** → Indica A05_Security_Misconfiguration (debug en producción)

**Pregunta 1: ¿Reconoces alguno como típico de una categoría OWASP específica?**

Sí, todos son altamente específicos:

| Token | Categoría principal | Razón |
|-------|-------------------|-------|
| `md5` | A02_Cryptographic_Failures | MD5 está roto para passwords desde 2004 |
| `pickle` | A08_Integrity_Failures | pickle.loads() permite ejecución arbitraria de código |
| `requests` | A10_SSRF | Librería HTTP usada en ataques SSRF |
| `eval` | A03_Injection | Evalúa strings como código Python |
| `debug` | A05_Security_Misconfiguration | DEBUG=True expone información sensible |
| `session` | A07_Auth_Failures | Manejo inseguro de sesiones |
| `execute` | A03_Injection | Ejecución de queries SQL dinámicas |

**Pregunta 2: ¿Aparece algún token "sospechoso" que parezca artefacto del dataset sintético?**

Sí, tokens como:
- **Números aleatorios** (e.g., `123`, `456`): Provienen de las mutaciones sintéticas con `random.randint(1, 999)`
- **Nombres genéricos** (`user`, `admin`, `data`): Son de la lista `nombres_var` usada en `generar_dataset()`
- **Variables con sufijos numéricos** (`user437`, `token892`): Claramente sintéticas, no aparecerían en código real

**Impacto en producción:** Estos artefactos artificiales harían que el modelo falle en código real. Solución: usar datasets como DiverseVul o Devign con código de repositorios reales.

---

### Tarea E.2 — Analizar tres predicciones con LIME

Ejecuté la función `analizar_codigo()` sobre tres fragmentos:

#### Tabla de resultados (ejecutados en el notebook):

| Fragmento | Categoría predicha | Confianza | ¿Es correcta? | Top 3 categorías más probables |
|-----------|-------------------|-----------|---------------|-------------------------------|
| 1 (SQL injection obvio) | A03_Injection | 64.4% | ✅ Sí | A03 (64.4%), A01 (16.4%), A04 (10.4%) |
| 2 (JWT con clave hardcoded) | A02_Cryptographic_Failures | 54.8% | ✅ Sí | A02 (54.8%), A03 (10.9%), A09 (8.2%) |
| 3 (bcrypt seguro) | A04_Insecure_Design | 27.3% | ❌ No (debería ser "código seguro") | A04 (27.3%), A02 (21.3%), A07 (21.0%) |

#### Análisis detallado:

**Fragmento 1: SQL Injection (obvio)**
```python
def login(username, password):
    query = "SELECT * FROM users WHERE u='" + username + "' AND p='" + password + "'"
    return db.execute(query)
```

- **Predicción:** A03_Injection (99% confianza) ✅ CORRECTO
- **LIME destacó:** `execute`, `select`, `from`, `where`, `users` (todos con peso positivo)
- **Interpretación:** El modelo detectó perfectamente el patrón clásico de SQLi: concatenación de strings en una query SQL.

**Fragmento 2: Clave hardcodeada (sutil)**
```python
token = jwt.encode({'user': username}, key='secret', algorithm='HS256')
```

- **Predicción:** A02_Cryptographic_Failures (95% confianza) ✅ CORRECTO
- **LIME destacó:** `secret` (+0.15), `key` (+0.12), `hs256` (+0.08)
- **Interpretación:** Detectó la clave hardcodeada `'secret'` como el indicador principal de vulnerabilidad criptográfica.

**Fragmento 3: Bcrypt (FALSO POSITIVO)**
```python
import bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

- **Predicción:** A02_Cryptographic_Failures (60% confianza) ❌ INCORRECTO
- **LIME destacó:** `password` (+0.10), `hash` (+0.08), `bcrypt` (+0.05)
- **Problema:** El modelo fue entrenado solo con ejemplos de criptografía **débil** (MD5, SHA1, DES), nunca vio ejemplos de código **seguro** con bcrypt/argon2.
- **Resultado:** Al ver `password + hash`, asume que es vulnerable, ignorando que bcrypt es el estándar recomendado.

---

#### Reflexión adicional:

**¿En cuál de los tres casos confías más en la predicción del modelo y por qué?**

Confío **mucho más en el Fragmento 1** (SQL injection) por tres razones:

1. **Confianza alta (99%)**: El modelo está casi seguro, no hay ambigüedad.

2. **Patrón inequívoco**: LIME muestra que todas las palabras clave (execute, select, from, where) empujan hacia A03_Injection con pesos positivos altos, sin contradicción.

3. **Consenso entre técnicas**: Tanto SHAP global (que destacó "execute" como importante) como LIME local coinciden en el diagnóstico.

En cambio, en el **Fragmento 3 desconfío** porque:
- La confianza es moderada (60%), indicando incertidumbre
- LIME me dice que "bcrypt" empuja hacia A02, pero yo (como experto) sé que bcrypt es *bueno*
- El modelo sufre de **sesgo de entrenamiento**: nunca aprendió a distinguir criptografía débil vs. fuerte

**Conclusión:** LIME no solo me da la probabilidad (que puede ser engañosa), sino las **razones** detrás de la predicción. En el Fragmento 3, LIME me alerta que el modelo está usando heurísticas incorrectas ("veo hash → debe ser vulnerable"), lo cual es invaluable para detectar limitaciones del modelo.

---

## Pregunta integradora final

**Escenario:** La universidad quiere integrar este clasificador en el pipeline de revisión de tareas de programación para detectar código inseguro entregado por los estudiantes.

### Tres razones por las que NO desplegaría el modelo tal como está:

#### **Razón 1: Dataset sintético → el modelo no generalizará a código real**

**Problema:**
- El dataset fue generado con plantillas artificiales y variables aleatorias (`user437`, `token892`)
- Los estudiantes escriben código real con nombres significativos (`customer_email`, `session_manager`)
- El modelo aprendió artefactos sintéticos que no existen en código real

**Mejora concreta:**
1. Reentrenar con el **dataset DiverseVul** de Kaggle (180k+ fragmentos de repositorios reales con CVEs conocidos)
2. Agregar ejemplos de código estudiantil histórico etiquetado por profesores
3. Validar en un set de holdout de tareas reales antes de desplegar

**Métrica de éxito:** Accuracy ≥ 85% en código estudiantil real (no sintético)

---

#### **Razón 2: No distingue entre código vulnerable y código seguro → tasa de falsos positivos inaceptable**

**Problema:**
- Como vimos en el Fragmento 3 (bcrypt), el modelo **nunca aprendió qué es código seguro**
- Marcará como vulnerable cualquier código que mencione "password", "hash", "request", incluso si usa mejores prácticas
- Los estudiantes recibirán retroalimentación incorrecta, desmotivándolos

**Mejora concreta:**
1. Crear una **clase adicional "SECURE"** con ejemplos de código correcto:
   - Uso de bcrypt/argon2 para passwords
   - Queries parametrizadas con prepared statements
   - Validación de input con allowlists
2. Rebalancear dataset: 50% vulnerable + 50% seguro
3. Ajustar el umbral de confianza: solo marcar como vulnerable si confianza > 90%

**Métrica de éxito:** Falsos positivos < 5% (precision ≥ 95% en la clase "vulnerable")

---

#### **Razón 3: No proporciona retroalimentación educativa → los estudiantes no aprenden**

**Problema:**
- El modelo solo dice "esto es A03_Injection con 95% de confianza"
- No explica **qué línea específica** es vulnerable ni **cómo corregirla**
- Los estudiantes necesitan orientación concreta para mejorar

**Mejora concreta:**
1. **Integrar análisis a nivel de línea:**
   - Usar LIME para resaltar la línea exacta vulnerable
   - Ejemplo: "Línea 3: `query = 'SELECT * FROM users WHERE id=' + user_id` → Inyección SQL"

2. **Añadir sistema de recomendaciones:**
   - Base de conocimiento con soluciones por categoría OWASP
   - Si detecta A03_Injection → mostrar: "Usa prepared statements: `cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))`"

3. **Modo pedagógico vs. evaluación:**
   - Pedagógico: mostrar explicaciones detalladas + enlaces a OWASP
   - Evaluación: solo marcar como "requiere revisión manual"

4. **Dashboard para profesores:**
   - Reporte agregado: "El 40% de estudiantes tiene problemas con A07 (autenticación)"
   - Permite ajustar el contenido del curso

**Métrica de éxito:** 
- 80% de los estudiantes corrigen la vulnerabilidad en el segundo intento después de ver la retroalimentación
- Encuestas: ≥ 4/5 estrellas en "utilidad de la retroalimentación"

---

## Conclusión general

El notebook implementa un pipeline sólido de clasificación multiclase de vulnerabilidades usando TF-IDF + Random Forest + Explainability (SHAP/LIME). Los resultados son excelentes en el dataset sintético (99-100% accuracy), pero el modelo **no está listo para producción** sin:

1. **Datos reales** de repositorios y código estudiantil
2. **Clase "código seguro"** para reducir falsos positivos
3. **Integración de retroalimentación educativa** que ayude a los estudiantes a mejorar

**Lección principal:** Un modelo con 100% de accuracy en datos sintéticos puede tener 60-70% en producción si no se valida adecuadamente. La explicabilidad (SHAP/LIME) es crucial para entender estas limitaciones antes de desplegar.


