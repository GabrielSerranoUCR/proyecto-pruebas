## Evidencias de configuracion supabase

### Configuración del Supabase

Se accede al pagina oficial de Supabase y se crea un proyecto, se selecciona la región america y se le asigna un nombre al proyecto.

Pagina oficial: [https://supabase.com/](https://supabase.com/)

Captura:
![alt text](image.png)

**Explicación**: Se crea el proyecto en Supabase Proyecto Pruebas dentro de la Organizacion Pruebas de Software. 

### Instalación/configuración del cliente de Supabase

Captura:

**Doc oficial supabase**
![alt text](image-1.png)

**Ejecucion de terminal con uv**
![alt text](image-2.png)

**Se crea tabla de prueba en supabase**
![alt text](image-3.png)

**Se toma codigo de ejemplo y se adapta para prueba de conexión**
![alt text](image-4.png)


**Se realiza primera prueba, falla por no tener permisos**
![alt text](image-5.png)

**Se configura la tabla para permitir lectura a todos los usuarios**
![alt text](image-6.png)

**Operacion de select exitosa**
![alt text](image-7.png)


### Configuración de las variables de entorno

Captura:
![alt text](image-8.png)

Explicación:
Se configuran las variables de entorno en el archivo .env, se agregan las variables SUPABASE_URL y SUPABASE_KEY con los valores obtenidos del proyecto en supabase, tambien se podrian definir como variables de entorno del sistema operativo, pero se opta por definirlas en el archivo .env para que sean cargadas automaticamente al ejecutar el proyecto.