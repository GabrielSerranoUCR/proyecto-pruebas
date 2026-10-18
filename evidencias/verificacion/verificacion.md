### Versión de Python

**Captura:**
<br>
![alt text](image.png)

**Explicación:**
<br>
Se usa python 3.13.7, definida en el archivo .python-version, que es la versión que se instala al ejecutar `uv sync` y que se usa para crear el ambiente virtual del proyecto.

### Versión de pip/UV

**Captura:**
<br>
![alt text](image-1.png)

**Explicación:**
<br>
Se usa uv 0.12.15, que era la ultima versión disponible al momento de la instalación.

### Importación exitosa de las librerías

**Captura:**
<br>
![alt text](image-2.png)

**Explicación:**
<br>
Se importan exitosamente las librerías necesarias para el proyecto, incluyendo scipy, scikit-learn y pytest.

### Ejecución de Pytest

**Captura:**
<br>
![alt text](image-3.png)

**Explicación:**
<br>
Se ejecuta Pytest exitosamente, lo que indica que las pruebas unitarias están funcionando correctamente.

### Ejecución de Pylint

**Captura:**
<br>
![alt text](image-4.png)

  **Explicación:**
<br>
Se ejecuta Pylint exitosamente, aunque da warnings, por ahora que es de prueba de conexion, se deja asi.

### Conexión exitosa con Supabase

**Captura:**
<br>
![alt text](image-5.png)

**Explicación:**
<br>
Se establece una conexión exitosa con Supabase, lo que indica que el entorno está correctamente configurado.

### Ejecución de una operación de prueba sobre Supabase

**Captura:**
<br>
![alt text](image-5.png)

**Explicación:**
<br>
Se realiza una operación de prueba (select) sobre la tabla "users_test" en Supabase, y se obtiene una respuesta exitosa, lo que confirma que la conexión y la configuración de Supabase son correctas.
