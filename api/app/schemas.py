from typing import List, Optional

from pydantic import BaseModel, Field

from . import config


class SolicitudBusqueda(BaseModel):
    """Cuerpo de la petición POST /buscar."""

    consulta: str = Field(
        ..., min_length=2, description="Texto de búsqueda: habilidades, cargo, etc."
    )
    k_plantillas: int = Field(
        5, ge=1, le=config.MAX_K_PLANTILLAS,
        description="Cuántas plantillas de texto distintas considerar como relevantes.",
    )
    max_resultados: int = Field(
        20, ge=1, le=config.MAX_RESULTADOS,
        description="Máximo de ofertas individuales a devolver.",
    )

    # Filtros exactos
    pais: Optional[str] = Field(None, description="Filtra por país exacto, p. ej. 'Colombia'.")
    modalidad: Optional[str] = Field(
        None, description="Filtra por modalidad de trabajo exacta, p. ej. 'Full-Time'."
    )

    # Filtros por rango (numéricos)
    experiencia_min: Optional[int] = Field(
        None, ge=0,
        description="Años de experiencia del candidato; se devuelven ofertas cuyo rango "
                     "[Experience min, Experience max] lo incluye.",
    )
    salario_min: Optional[int] = Field(
        None, ge=0, description="Salario mínimo deseado, en miles de USD."
    )
    salario_max: Optional[int] = Field(
        None, ge=0, description="Salario máximo deseado, en miles de USD."
    )


class OfertaResultado(BaseModel):
    job_id: int = Field(..., alias="Job Id")
    job_title: str = Field(..., alias="Job Title")
    role: str = Field(..., alias="Role")
    country: str = Field(..., alias="Country")
    work_type: str = Field(..., alias="Work Type")
    salary_range: str = Field(..., alias="Salary Range")
    experience: str = Field(..., alias="Experience")
    company: str = Field(..., alias="Company")
    similitud: float

    model_config = {"populate_by_name": True}


class RespuestaBusqueda(BaseModel):
    consulta: str
    total_resultados: int
    resultados: List[OfertaResultado]
