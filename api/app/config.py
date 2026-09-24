"""
Configuración de la API, leída desde variables de entorno.

En local: crea un archivo .env (ver .env.example) y usa `python-dotenv`,
o exporta las variables directamente en tu shell.

En Railway: se configuran como "Variables" del servicio, desde el dashboard.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env (si existe) hacia el entorno.
# En Railway esto no hace nada (no hay .env ahí), porque las variables ya
# vienen inyectadas directamente en el entorno del contenedor.
load_dotenv()

# --- Pinecone ---
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise RuntimeError(
        "Falta la variable de entorno PINECONE_API_KEY. "
        "Copia .env.example a .env, complétala con tu API key de Pinecone, "
        "y asegúrate de correr uvicorn desde la carpeta api/ (donde está el .env)."
    )
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "ofertas-laborales")

# --- Modelo de embeddings ---
# Debe ser el mismo con el que se generaron los vectores subidos a Pinecone
# (decisión final tomada en 05_Evaluacion_Metricas.ipynb: all-MiniLM-L6-v2)
MODELO_EMBEDDINGS = os.environ.get("MODELO_EMBEDDINGS", "all-MiniLM-L6-v2")

# --- Datos locales ---
# Estos parquet se generan en 02_Preprocesamiento.ipynb y 03_Embeddings_BusquedaVectorial.ipynb
# y deben copiarse a esta carpeta antes de levantar la API (ver README.md y descargar_datos.py)
DATA_DIR = Path(os.environ.get("DATA_DIR", str(Path(__file__).resolve().parent.parent / "data")))
RUTA_CLEAN = DATA_DIR / "job_descriptions_clean.parquet"
RUTA_MAPEO = DATA_DIR / "job_id_template_map.parquet"

# --- Límites de la API ---
MAX_K_PLANTILLAS = 20
MAX_RESULTADOS = 100
