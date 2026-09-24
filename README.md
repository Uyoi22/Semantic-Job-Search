# Semantic-Job-Search

Proyecto Integrador 1 - Deus Ex Code

participantes del grupo
- Simon Correa Rios
- Pablo Serna Valencia
- Juan Sebastian Andraus Lopez
- Isaac Cano Orozco

# API — Motor de Búsqueda Semántica de Ofertas Laborales

API en FastAPI que envuelve la lógica ya construida en los notebooks 03/04:
codifica la consulta con `all-MiniLM-L6-v2`, busca las plantillas más
similares en Pinecone, expande a ofertas reales y aplica filtros
(exactos y por rango) sobre el dataset limpio.

## 1. Estructura

```
api/
├── app/
│   ├── main.py       # endpoints de FastAPI
│   ├── search.py      # lógica de búsqueda (equivalente a buscar_ofertas_pinecone)
│   ├── schemas.py      # validación de entrada/salida (Pydantic)
│   └── config.py      # variables de entorno
├── data/                # AQUÍ van los parquet (no se suben al repo, ver paso 3)
├── descargar_datos.py  # opcional: baja los parquet desde Drive
├── requirements.txt
├── Dockerfile
└── .env.example
```

## 2. Configuración

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv/Scripts/activate
pip install -r requirements.txt

cp .env.example .env
# Edita .env y pon tu PINECONE_API_KEY real (la misma que usaron en 04_BaseDatosVectorial.ipynb)
```

## 3. Obtener los datos

La API necesita dos archivos que ya generaron en Colab (en
`proyecto_integrador/data/processed/` dentro de Google Drive):

- `job_descriptions_clean.parquet`
- `job_id_template_map.parquet`

**Opción A — copiar a mano:** descárgalos de Drive y ponlos dentro de `api/data/`.

**Opción B — script automático:** en Drive, clic derecho sobre cada archivo →
"Obtener enlace" → "Cualquiera con el enlace", copia el ID del archivo (la
parte de la URL entre `/d/` y `/view`), ponlo en `.env` como
`DRIVE_FILE_ID_CLEAN` / `DRIVE_FILE_ID_MAPEO`, y corre:

```bash
python descargar_datos.py
```

No hace falta ni el índice FAISS ni el `.npy` de embeddings — esos ya están
"vivos" dentro de Pinecone, la API solo necesita los datos tabulares.

## 4. Correr localmente

```bash
uvicorn app.main:app --reload
```

Abre `http://localhost:8000/docs` — FastAPI genera ahí mismo documentación
interactiva (Swagger) donde se puede probar `/buscar` directo desde el
navegador, sin necesidad de Postman ni curl.

### Ejemplo de petición

```bash
curl -X POST http://localhost:8000/buscar \
  -H "Content-Type: application/json" \
  -d '{
    "consulta": "python developer with machine learning and NLP experience",
    "k_plantillas": 5,
    "max_resultados": 10,
    "modalidad": "Full-Time",
    "experiencia_min": 3
  }'
```

## 5. Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Chequeo simple de que el servicio está arriba |
| POST | `/buscar` | Búsqueda semántica con filtros opcionales |
| GET | `/filtros/paises` | Lista de países disponibles (para poblar un dropdown en el frontend) |
| GET | `/filtros/modalidades` | Lista de modalidades de trabajo disponibles |

### Cuerpo de `/buscar`

```json
{
  "consulta": "string (obligatorio)",
  "k_plantillas": 5,
  "max_resultados": 20,
  "pais": "Colombia",
  "modalidad": "Full-Time",
  "experiencia_min": 3,
  "salario_min": 50,
  "salario_max": 100
}
```

`experiencia_min` se interpreta como "años de experiencia del candidato" —
la API devuelve ofertas cuyo rango `[experiencia_min, experiencia_max]` lo
cubre. `salario_min`/`salario_max` están en miles de USD (mismo formato que
`Salary Range` en el dataset original, p. ej. `$59K-$99K`).

## 6. Desplegar en Railway

1. Sube esta carpeta `api/` a un repositorio de GitHub (agrega un `.gitignore`
   con `.venv/`, `.env` y `data/*.parquet` — los parquet no deberían ir al
   repo por tamaño).
2. En Railway: *New Project* → *Deploy from GitHub repo*, seleccionando este repo.
   Railway detecta el `Dockerfile` automáticamente.
3. En la pestaña *Variables* del servicio, agrega: `PINECONE_API_KEY`,
   `PINECONE_INDEX_NAME`, y (si usan la Opción B) `DRIVE_FILE_ID_CLEAN` /
   `DRIVE_FILE_ID_MAPEO`.
4. Si usan la Opción B, agrega `python descargar_datos.py &&` al inicio del
   *Start Command* en Railway, antes de `uvicorn app.main:app ...`, para que
   los datos se descarguen automáticamente en cada despliegue.
5. Railway te da una URL pública (`https://tu-proyecto.up.railway.app`) — esa
   es la que va a consumir el prototipo de interfaz web.

## 7. Pendientes / próximos pasos

- Agregar autenticación básica o un API key propio si la API queda expuesta
  públicamente antes de la sustentación.
- Cachear resultados de consultas repetidas (por ejemplo con `functools.lru_cache`
  sobre `buscar_ofertas`) si en la demo hacen muchas búsquedas iguales.
- Conectar el prototipo de interfaz (Streamlit u otro) a esta API en vez de
  llamar la lógica de búsqueda directamente.
