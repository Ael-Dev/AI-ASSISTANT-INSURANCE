"""Esquema de un cliente del CSV AutoInsurance. Valida y renombra las columnas."""

# Para interpretar fechas
from datetime import datetime

# Permite agregar reglas a un tipo
from typing import Annotated

# Herramientas de validación de Pydantic
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

# Formato del identificador, ej: BU79786. El dataset incluye algunos con minúscula como No36572
# Texto con dos letras y cinco dígitos
CustomerIdentifier = Annotated[str, StringConstraints(pattern=r"^[A-Za-z]{2}\d{5}$")]


# Un cliente del CSV
class Customer(BaseModel):
    """Una fila del CSV. Los alias son los nombres originales de las columnas."""

    # Permite usar el nombre del campo además del alias
    model_config = ConfigDict(populate_by_name=True)

    # Identificador del cliente
    customer_id: CustomerIdentifier = Field(alias="Customer")
    # Estado de residencia
    state: str = Field(alias="State")
    # Valor del cliente a lo largo del tiempo
    customer_lifetime_value: float = Field(alias="Customer Lifetime Value")
    # Respuesta a la última oferta
    response: str = Field(alias="Response")
    # Nivel de cobertura
    coverage: str = Field(alias="Coverage")
    # Nivel educativo
    education: str = Field(alias="Education")
    # Fecha de vigencia en formato ISO
    effective_to_date: str = Field(alias="Effective To Date")
    # Situación laboral
    employment_status: str = Field(alias="EmploymentStatus")
    # Género
    gender: str = Field(alias="Gender")
    # Ingreso
    income: int = Field(alias="Income")
    # Tipo de zona de residencia
    location_code: str = Field(alias="Location Code")
    # Estado civil
    marital_status: str = Field(alias="Marital Status")
    # Prima mensual del seguro
    monthly_premium_auto: int = Field(alias="Monthly Premium Auto")
    # Meses desde el último reclamo
    months_since_last_claim: int = Field(alias="Months Since Last Claim")
    # Meses desde que inició la póliza
    months_since_policy_inception: int = Field(alias="Months Since Policy Inception")
    # Quejas abiertas
    number_of_open_complaints: int = Field(alias="Number of Open Complaints")
    # Cantidad de pólizas
    number_of_policies: int = Field(alias="Number of Policies")
    # Tipo de póliza
    policy_type: str = Field(alias="Policy Type")
    # Nivel de póliza
    policy: str = Field(alias="Policy")
    # Tipo de oferta de renovación
    renew_offer_type: str = Field(alias="Renew Offer Type")
    # Canal de venta
    sales_channel: str = Field(alias="Sales Channel")
    # Monto total reclamado
    total_claim_amount: float = Field(alias="Total Claim Amount")
    # Clase de vehículo
    vehicle_class: str = Field(alias="Vehicle Class")
    # Tamaño del vehículo
    vehicle_size: str = Field(alias="Vehicle Size")

    # Se ejecuta al validar la fecha
    @field_validator("effective_to_date")
    # Método que no depende de una instancia
    @classmethod
    # Unifica los formatos de fecha
    def convert_date_to_iso_format(cls, raw_date: str) -> str:
        """El CSV mezcla 2/24/11 (mes primero) y 02-04-2011 (día primero). Se unifica a ISO."""
        # Prueba cada formato de fecha conocido
        for date_format in ("%m/%d/%y", "%d-%m-%Y"):
            # Intenta interpretar la fecha con este formato
            try:
                # Devuelve la fecha como AAAA-MM-DD
                return datetime.strptime(raw_date, date_format).date().isoformat()
            # Si el formato no coincide
            except ValueError:
                # Prueba con el siguiente formato
                continue
        # Rechaza la fila si ningún formato sirve
        raise ValueError(f"Formato de fecha no reconocido: {raw_date}")
