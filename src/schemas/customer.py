"""Esquema de un cliente del CSV AutoInsurance. Valida y renombra las columnas."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

# Formato del identificador, ej: BU79786. El dataset incluye algunos con minúscula como No36572
CustomerIdentifier = Annotated[str, StringConstraints(pattern=r"^[A-Za-z]{2}\d{5}$")]


class Customer(BaseModel):
    """Una fila del CSV. Los alias son los nombres originales de las columnas."""

    model_config = ConfigDict(populate_by_name=True)

    customer_id: CustomerIdentifier = Field(alias="Customer")
    state: str = Field(alias="State")
    customer_lifetime_value: float = Field(alias="Customer Lifetime Value")
    response: str = Field(alias="Response")
    coverage: str = Field(alias="Coverage")
    education: str = Field(alias="Education")
    effective_to_date: str = Field(alias="Effective To Date")
    employment_status: str = Field(alias="EmploymentStatus")
    gender: str = Field(alias="Gender")
    income: int = Field(alias="Income")
    location_code: str = Field(alias="Location Code")
    marital_status: str = Field(alias="Marital Status")
    monthly_premium_auto: int = Field(alias="Monthly Premium Auto")
    months_since_last_claim: int = Field(alias="Months Since Last Claim")
    months_since_policy_inception: int = Field(alias="Months Since Policy Inception")
    number_of_open_complaints: int = Field(alias="Number of Open Complaints")
    number_of_policies: int = Field(alias="Number of Policies")
    policy_type: str = Field(alias="Policy Type")
    policy: str = Field(alias="Policy")
    renew_offer_type: str = Field(alias="Renew Offer Type")
    sales_channel: str = Field(alias="Sales Channel")
    total_claim_amount: float = Field(alias="Total Claim Amount")
    vehicle_class: str = Field(alias="Vehicle Class")
    vehicle_size: str = Field(alias="Vehicle Size")

    @field_validator("effective_to_date")
    @classmethod
    def convert_date_to_iso_format(cls, raw_date: str) -> str:
        """El CSV mezcla 2/24/11 (mes primero) y 02-04-2011 (día primero). Se unifica a ISO."""
        for date_format in ("%m/%d/%y", "%d-%m-%Y"):
            try:
                return datetime.strptime(raw_date, date_format).date().isoformat()
            except ValueError:
                continue
        raise ValueError(f"Formato de fecha no reconocido: {raw_date}")
