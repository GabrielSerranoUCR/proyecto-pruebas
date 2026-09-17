<!-- Portada -->
<div align="center">

# Universidad de Costa Rica

### Pruebas de software

<br>

## Informe: Etapa 1

<br>

**Integrantes:**
<br>
Angel Mena Coudin | C34789
<br>
Gabriel Serrano Rojas | C17497
<br>
Juan José Víquez Ríos | C38567
<br>
Josué Torres Sibaja | C37853
<br>
Rolando Villavicencio Gonzales | C28489

<br>

**Año:**
<br>
2026

</div>

## Introducción



## Objetivos

El objetivo del proyecto es someter la aplicación a un proceso de pruebas, aplicando de forma práctica los conocimientos, estándares, modelos y herramientas de las pruebas de software. Esto incluye principios de pruebas, gestión del proceso de pruebas, verificación y validación, entre otros conceptos clave para evaluar y garantizar la calidad del sistema.

## Descripción

**Problema a abordar:**
<br>
Asegurar la calidad del código por medio de pruebas

**Funcionalidades a probar:**
<br>

**Alcance inicial:**
<br>

## Repositorio Git

### Dirección del repositorio

**URL:**
<br>
[Elance al repositorio](https://github.com/GabrielSerranoUCR/proyecto-pruebas/tree/main)

**Explicación:**
<br>
URL a un repositorio remoto en github.

### Estructura

**Diagrama:**
<br>
```text
proyecto-pruebas/
├── docs/
│   └── ...
├── evidencias/
│   ├── diseño_de_pruebas/
│   ├── instalacion/
│   ├── plan_de_pruebas/
│   ├── repositorio/
│   └── verificacion/
├── src/
│   └── proyecto_pruebas/
├── tests/
└── README.md
```

**Explicación:**
<br>
La estructura actual está basada en la recomendación del profesor. Con ligeras alteraciones al no hacer uso de requirements.txt, ya que vamos a utilizar la herramienta uv para gestionar los paquetes y el proyecto.

Por otro lado, la carpeta de evidencia se descompone en carpetas específicas para cada evidencia solicitada.

### Archivos iniciales

**Captura:**
<br>
![archivos iniciales imagen](../evidencias/repositorio/archivos_init.png)

**Explicación:**
<br>
Los archivos iniciales son específicamente archivos git y archivos relacionados a UV, que se generan automáticamente, necesarios para que el ambiente funcione.

### Commits realizados

Se pueden visualizar en el repositorio

## Plan de Trabajo

El plan de trabajo se armó en un google sheets que se puede visualizar desde el siguiente enlace:

[Ver plan de trabajo](https://docs.google.com/spreadsheets/d/1IGmu08bjfda4OAQALcscwWfYLhLuleYi6xQ7R213txM/edit?gid=0#gid=0)

No es la versión final, se va ir actualizando conforme se vaya definiendo las cargas de trabajo del proyecto.

## Plan Inicial de Pruebas

### 1. Alcance

**Qué se probará.** La solución mínima construida por el equipo, que integra los tres
modelos asignados:

- **M07 — Riesgo de diabetes** (Salud, clasificación binaria)
- **M08 — Monto de préstamo** (Finanzas, regresión)
- **M09 — Riesgo académico** (Educación, clasificación multiclase)

expuestos mediante una API que valida el contrato y orquesta la
predicción, una interfaz de usuario que captura los parámetros y
presenta el resultado, y persistencia de solicitudes/resultados en
Supabase/PostgreSQL.

#### Funcionalidades objeto de prueba

**Interfaz**
<br>
- Selección del modelo y despliegue del formulario correspondiente a sus
  parámetros.
- Captura de los parámetros de entrada de cada modelo.
- Validación de las entradas escritas en la página web, antes de enviar la
  solicitud a la API.
- Presentación del resultado.
- Manejo y presentación de los errores devueltos por la API.

**API**
<br>
- Validación del contrato de entrada por modelo, independiente de la
  validación hecha en la interfaz.
- Invocación del modelo correspondiente según la ruta/endpoint solicitado.
- Devolución de la respuesta con la estructura del contrato: fecha, hora,
  modelo, predicción, métrica e id_ejecucion.
- Manejo de errores con los códigos HTTP correspondientes.
- Seguridad básica de las rutas expuestas: entradas maliciosas y exposición
  de información sensible.

**Modelos**
<br>
- Cálculo de la predicción para cada uno de los tres modelos.
- Manejo de valores extremos o inesperados.
- Precisión numérica del resultado, incluyendo el redondeo (en particular
  para M08, que devuelve un monto).

**Base de datos**
<br>
- Almacenamiento de la ejecución y su resultado.
- Consulta del historial de ejecuciones almacenado.
- Comportamiento del sistema cuando la base de datos no está disponible.

**Fuera de alcance**
<br>
- Pruebas de carga o rendimiento bajo volumen alto de solicitudes.
- Autenticación y autorización de usuarios.
- Despliegue en un ambiente de producción.
- Automatización de pruebas de UI end-to-end (por ahora se contemplan
  pruebas manuales de usabilidad).

**Limitaciones conocidas**
<br>
- El desarrollo se encuentra en fase inicial: solo el esqueleto del
  repositorio y el ambiente están configurados. La API, el UI y los tres
  modelos aún no están implementados, por lo que este diseño es preliminar y
  se refinará en las siguientes etapas.

### 2. Riesgos

| Riesgo                                                                                                   | Probabilidad | Impacto | Mitigación                                                                                              |
| -------------------------------------------------------------------------------------------------------- | ------------ | ------- | ------------------------------------------------------------------------------------------------------- |
| Supabase no disponible o mal configurado                                                                 | Media        | Alto    | Verificar la conexión al inicio de cada sesión de trabajo; documentar el procedimiento de configuración |
| Cambios en el contrato de la API durante el desarrollo                                                   | Alta         | Alto    | Mantener el contrato documentado y bajo control de versiones; automatizar pruebas de contrato           |
| Inconsistencia entre los tres tipos de modelo (binario, regresión, multiclase) en la respuesta de la API | Media        | Medio   | Definir un contrato de respuesta común y validar cada tipo por separado                                 |
| Disponibilidad desigual de los integrantes del equipo                                                    | Media        | Medio   | Repartir tareas pequeñas y verificables (roles pendientes de asignar)                                   |
| Tiempo insuficiente antes de la entrega final (20 de noviembre)                                          | Media        | Alto    | Priorizar la automatización mínima exigida y avanzar de forma incremental por etapa                     |

### 3. Estrategia

La estrategia recorre los niveles de la **pirámide de pruebas**:
<br>
unitarias → integración → funcionales/sistema → aceptación, combinando
**Verificación** (revisiones, análisis estático, pruebas unitarias) y
**Validación** (pruebas funcionales y de aceptación) en cada fase.

Se aplicarán pruebas funcionales positivas y negativas en partes iguales,
siguiendo la **regla del 50/50**:
<br>
la mitad de los casos valida que
el sistema haga lo que debe, la otra mitad que no haga lo que no debe. Se
complementan con pruebas de integración (UI→API, API→modelo, API→Supabase y
el flujo completo) y no funcionales básicas (usabilidad, confiabilidad,
seguridad).

El laboratorio de ML visto en clase añade dos categorías propias de
sistemas de ML:
<br>
**pruebas de validez de datos** (que la entrada cumpla
formato, tipo y rango esperado, tanto antes del preprocesamiento como en
el contrato de la API) y **pruebas de calidad del modelo** (que las
métricas de cada modelo, sección 7, no se degraden por debajo de un
umbral mínimo aceptable).

Manuales y automatizadas se complementan, no compiten. Se
automatizarán con pytest las pruebas unitarias de cada modelo, las pruebas
de contrato de la API (positivas y negativas), la integración API→modelo,
la persistencia API→Supabase y al menos un caso de borde, cumpliendo el
mínimo de automatización exigido por el proyecto. Se ejecutarán de forma
manual las pruebas de usabilidad de la interfaz, la exploración del flujo
completo UI→API→modelo→Supabase y las pruebas no funcionales de
confiabilidad ante indisponibilidad y seguridad básica.

Como **prueba estática** se incluye análisis estático automatizado
(Pylint sobre `src/`). Cada caso de prueba del Diseño de Pruebas deberá declarar un **oráculo explícito**, sin el cual no se puede concluir si la prueba pasó o falló.

#### Técnicas de diseño aplicadas (Caja Negra, mínimo 3)

1. **Partición de equivalencia**: agrupa valores válidos e inválidos de
  los parámetros de entrada de cada modelo (ej. edad, ingresos, notas).
2. **Análisis de valores límite**: prueba los límites de rangos numéricos
  relevantes (edad mínima/máxima, montos de préstamo, notas límite del
  riesgo académico).
3. **Pruebas basadas en riesgo**: prioriza, entre los tres modelos, los
  flujos con mayor probabilidad o impacto de fallo.

### 4. Criterios

#### Criterios de entrada
- Contrato de API definido y documentado para los tres modelos.
- Ambiente de desarrollo configurado y verificado (Python, dependencias,
  Supabase).
- Modelos accesibles (entrenados o con lógica mínima de predicción).
- Plan de Pruebas y Diseño de Pruebas completos, con los datos de prueba
  definidos y los casos priorizados (cada uno con su resultado esperado).

#### Criterios de salida
- Casos de prueba ejecutados y resultados registrados para los tres
  modelos.
- Defectos registrados en GitHub Issues (severidad, prioridad, pasos,
  evidencia).
- Retests completados y regresión aplicada donde corresponda.
- Métricas calculadas y trazabilidad actualizada.
- Recomendación Go/No-Go sustentada (a emitir en una etapa posterior).

### 5. Recursos

#### Humanos

| Nombre | % de participación | Asignación |
|---|---|---|
| Angel Mena Coudin | 100% | Pendiente |
| Gabriel Serrano Rojas | 100% | Pendiente |
| Juan José Víquez Ríos | 100% | Pendiente |
| Josué Torres Sibaja | 100% | Pendiente |
| Rolando Villavicencio González | 100% | Pendiente |

> Los integrantes participarán de forma transversal en todas las
> actividades del proyecto (análisis, desarrollo, pruebas,
> documentación), sin roles fijos por componente.

- **Hardware**: equipo de cómputo personal de cada integrante.
- **Software y versión de Python**: Python 3.13+, gestionado con `uv`.
- **Librerías**: scipy, scikit-learn, pytest, pylint (ya instaladas); se
  agregarán las del framework de API, de UI y el cliente de Supabase.
- **Herramientas**: Git/GitHub, GitHub Issues (registro de defectos),
  Pylint (análisis estático).
- **Datos de prueba**: datasets por modelo (M07, M08, M09), proporcionados
  por el docente.
- **Ambiente de desarrollo**: entorno virtual gestionado por `uv`
  (`.venv`), variables de entorno vía `.env`.
- **Infraestructura adicional**: proyecto de Supabase (PostgreSQL en la
  nube).

### 6. Cronograma

*Pendiente, depende de las fechas definidas en el plan de trabajo.*

### 7. Métricas

Los defectos se clasificarán por **severidad** (impacto técnico) y
**prioridad** (urgencia de corrección) de forma independiente.

#### Métricas propias de cada modelo

**Propósito:** confirmar que la predicción de cada modelo es confiable antes de sustentar su Go/No-Go:

- M07 (riesgo de diabetes, clasificación binaria): accuracy, precision,
  recall, F1.
- M08 (monto de préstamo, regresión): MAE, MSE/RMSE, R².
- M09 (riesgo académico, clasificación multiclase): accuracy, precision,
  recall, F1, matriz de confusión.

#### Métricas del proceso de pruebas

**Propósito:** medir el avance y la calidad del proceso de pruebas para monitorear su progreso:

- Porcentaje de casos ejecutados, aprobados y fallidos.
- Cobertura funcional y cobertura negativa.
- Cantidad de defectos por severidad y por componente.
- Porcentaje de pruebas automatizadas.

## Diseño inicial de Pruebas

[Ver evidencia del Diseño incial de pruebas](../evidencias/diseño_de_pruebas/diseño_de_pruebas.md)

## Instalación del ambiente de Pruebas

### Instalación de Python

**Captura:**
<br>
![alt text](../evidencias/instalacion_de_entorno/image-1.png)

**Explicación**:
<br>
No se instala python directamente, sino que se instala uv, el mismo se encarga de instalar la versión de python que se necesita para el proyecto y las dependencias necesarias para el proyecto.

### Creación del proyecto en UV (Creación del entorno virtual, instalación de dependencias y archivo de requirements.txt)

**Captura:**
<br>
![alt text](../evidencias/instalacion_de_entorno/image.png)

**Explicación:**
<br>
Se hace la syncronización del proyecto con uv, el mismo se encarga de crear el entorno virtual y se instalan las dependencias necesarias para el proyecto.

## Verificación del ambiente

### Versión de Python

**Captura:**
<br>
![alt text](../evidencias/verificacion/image.png)

**Explicación:**
<br>
Se usa python 3.13.7, definida en el archivo .python-version, que es la versión que se instala al ejecutar `uv sync` y que se usa para crear el ambiente virtual del proyecto.

### Versión de pip/UV

**Captura:**
<br>
![alt text](../evidencias/verificacion/image-1.png)

**Explicación:**
<br>
Se usa uv 0.12.15, que era la ultima versión disponible al momento de la instalación.

### Importación exitosa de las librerías

**Captura:**
<br>
![alt text](../evidencias/verificacion/image-2.png)

  **Explicación:**
<br>
Se importan exitosamente las librerías necesarias para el proyecto, incluyendo scipy, scikit-learn y pytest.

### Ejecución de Pytest

**Captura:**
<br>
![alt text](../evidencias/verificacion/image-3.png)

**Explicación:**
<br>
Se ejecuta Pytest exitosamente, lo que indica que las pruebas unitarias están funcionando correctamente.

### Ejecución de Pylint

**Captura:**
<br>
![alt text](../evidencias/verificacion/image-4.png)

**Explicación:**
<br>
Se ejecuta Pylint exitosamente, aunque da warnings, por ahora que es de prueba de conexion, se deja asi.

### Conexión exitosa con Supabase

**Captura:**
<br>
![alt text](../evidencias/verificacion/image-5.png)

**Explicación:**
<br>
Se establece una conexión exitosa con Supabase, lo que indica que el entorno está correctamente configurado.

### Ejecución de una operación de prueba sobre Supabase

**Captura:**
<br>
![alt text](../evidencias/verificacion/image-5.png)

**Explicación:**
<br>
Se realiza una operación de prueba (select) sobre la tabla "users_test" en Supabase, y se obtiene una respuesta exitosa, lo que confirma que la conexión y la configuración de Supabase son correctas.

## Conclusiones



## Referencias
