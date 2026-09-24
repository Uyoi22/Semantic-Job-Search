"""
Motor de búsqueda: misma lógica que `buscar_ofertas_pinecone()` en
03_Embeddings_BusquedaVectorial.ipynb / 04_BaseDatosVectorial.ipynb, adaptada
para vivir en un servicio de larga duración (FastAPI) en vez de un notebook.

Los recursos pesados (modelo, cliente de Pinecone, dataset) se cargan UNA VEZ
al arrancar el proceso (ver `cargar_recursos`), no en cada petición.
"""
from typing import Optional

import pandas as pd
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from . import config

_modelo: Optional[SentenceTransformer] = None
_pinecone_index = None
_df_clean: Optional[pd.DataFrame] = None


def cargar_recursos() -> None:
    """Carga el modelo, el índice de Pinecone y el dataset en memoria. Se llama al arrancar la API."""
    global _modelo, _pinecone_index, _df_clean

    if not config.RUTA_CLEAN.exists() or not config.RUTA_MAPEO.exists():
        raise FileNotFoundError(
            f"Faltan datos en {config.DATA_DIR}. Se esperan "
            f"'{config.RUTA_CLEAN.name}' y '{config.RUTA_MAPEO.name}'. "
            "Corre descargar_datos.py o copia los archivos manualmente (ver README.md)."
        )

    _modelo = SentenceTransformer(config.MODELO_EMBEDDINGS)

    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    _pinecone_index = pc.Index(config.PINECONE_INDEX_NAME)

    df_clean = pd.read_parquet(config.RUTA_CLEAN)
    mapeo = pd.read_parquet(config.RUTA_MAPEO)
    _df_clean = df_clean.merge(mapeo, on="Job Id", how="left")


def _asegurar_recursos_cargados() -> None:
    if _modelo is None or _pinecone_index is None or _df_clean is None:
        cargar_recursos()


def buscar_ofertas(
    consulta: str,
    k_plantillas: int = 5,
    max_resultados: int = 20,
    pais: Optional[str] = None,
    modalidad: Optional[str] = None,
    experiencia_min: Optional[int] = None,
    salario_min: Optional[int] = None,
    salario_max: Optional[int] = None,
) -> list[dict]:
    _asegurar_recursos_cargados()

    # 1. Codificar la consulta y buscar plantillas relevantes en Pinecone
    vector_consulta = _modelo.encode(
        consulta, normalize_embeddings=True, convert_to_numpy=True
    ).tolist()

    respuesta = _pinecone_index.query(
        vector=vector_consulta, top_k=k_plantillas, include_metadata=False
    )
    template_ids = [int(match["id"]) for match in respuesta["matches"]]
    similitud_por_template = {int(m["id"]): m["score"] for m in respuesta["matches"]}

    # 2. Expandir a ofertas reales
    resultados = _df_clean[_df_clean["template_id"].isin(template_ids)].copy()
    resultados["similitud"] = resultados["template_id"].map(similitud_por_template)

    # 3. Filtros exactos
    if pais:
        resultados = resultados[resultados["Country"] == pais]
    if modalidad:
        resultados = resultados[resultados["Work Type"] == modalidad]

    # 4. Filtros por rango
    if experiencia_min is not None:
        resultados = resultados[
            (resultados["experiencia_min"] <= experiencia_min)
            & (resultados["experiencia_max"] >= experiencia_min)
        ]
    if salario_min is not None:
        resultados = resultados[resultados["salario_max"] >= salario_min]
    if salario_max is not None:
        resultados = resultados[resultados["salario_min"] <= salario_max]

    # 5. Ordenar y limitar
    resultados = resultados.sort_values("similitud", ascending=False)

    columnas = [
        "Job Id", "Job Title", "Role", "Country", "Work Type",
        "Salary Range", "Experience", "Company", "similitud",
    ]
    return resultados[columnas].head(max_resultados).to_dict(orient="records")


def listar_paises() -> list[str]:
    _asegurar_recursos_cargados()
    return sorted(_df_clean["Country"].dropna().unique().tolist())


def listar_modalidades() -> list[str]:
    _asegurar_recursos_cargados()
    return sorted(_df_clean["Work Type"].dropna().unique().tolist())
