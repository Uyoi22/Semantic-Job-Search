from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import search
from .schemas import RespuestaBusqueda, SolicitudBusqueda

app = FastAPI(
    title="Motor de Búsqueda Semántica de Ofertas Laborales",
    description="API del Proyecto Integrador 1 — Ingeniería de Sistemas",
    version="0.1.0",
)

# En producción, reemplazar "*" por el dominio real del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    # Carga el modelo, Pinecone y el dataset una sola vez, al arrancar el proceso
    search.cargar_recursos()


@app.get("/health", tags=["Sistema"])
def health() -> dict:
    return {"status": "ok"}


@app.post("/buscar", response_model=RespuestaBusqueda, tags=["Búsqueda"])
def buscar(solicitud: SolicitudBusqueda) -> dict:
    try:
        resultados = search.buscar_ofertas(
            consulta=solicitud.consulta,
            k_plantillas=solicitud.k_plantillas,
            max_resultados=solicitud.max_resultados,
            pais=solicitud.pais,
            modalidad=solicitud.modalidad,
            experiencia_min=solicitud.experiencia_min,
            salario_min=solicitud.salario_min,
            salario_max=solicitud.salario_max,
        )
    except Exception as exc:  # noqa: BLE001 - se traduce a un 500 legible para el cliente
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "consulta": solicitud.consulta,
        "total_resultados": len(resultados),
        "resultados": resultados,
    }


@app.get("/filtros/paises", tags=["Filtros"])
def paises() -> list[str]:
    return search.listar_paises()


@app.get("/filtros/modalidades", tags=["Filtros"])
def modalidades() -> list[str]:
    return search.listar_modalidades()
