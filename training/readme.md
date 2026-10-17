# Jupyter

## Instalación de Jupyter Notebook

Instalar la extensión de Jupyter Notebook en VS Code. Que sea oficial de Microsoft.

Para que el notebook funcione, ejecutar el siguiente comando en la terminal:

```bash
uv sync --group jupyter   
```

## Configuración del kernel de Jupyter Notebook

El archivo `pyproject.toml` ya trae las dependencias necesarias para que el notebook funcione. El comando anterior configura el entorno virtual con las dependencias requeridas. Por lo que se recomienda utilizar el entorno virtual creado con uv al seleccionar el kernel en Jupyter.


## Exportar modelo

Para utilizar el modelo, es necesario exportarlo. Con ejecutar el notebook `Diabetes_model.ipynb` se exportará el modelo a un archivo llamado `random_forest_model.joblib` en la carpeta `training/models/`.