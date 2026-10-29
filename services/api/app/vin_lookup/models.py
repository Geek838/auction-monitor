"""Bounded contracts: a decoded VIN does not establish auction or physical identity."""
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VinDecodeRequest(Contract):
    vin: str = Field(min_length=17, max_length=17, pattern=r"^[A-HJ-NPR-Z0-9]{17}$")

    @field_validator("vin", mode="before")
    @classmethod
    def normalize_vin(cls, value):
        return value.strip().upper() if isinstance(value, str) else value


class DecodedVehicle(Contract):
    year: int | None = None
    make: str | None = None
    model: str | None = None


class DecodeError(Contract):
    code: str
    description: str


class VinDecodeReport(Contract):
    schema_version: Literal["vin-decode-v1"] = "vin-decode-v1"
    vin: str
    outcome: Literal["DECODED", "PARTIAL", "UNAVAILABLE", "INVALID_VIN"]
    source: Literal["NHTSA_VPIC"] = "NHTSA_VPIC"
    source_url: str
    retrieved_at: AwareDatetime
    identity_status: Literal["NOT_AUCTION_VERIFIED"] = "NOT_AUCTION_VERIFIED"
    vehicle: DecodedVehicle = Field(default_factory=DecodedVehicle)
    errors: list[DecodeError] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
