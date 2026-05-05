"""Vendor-related schema models for Indian procurement context.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class VendorBase(BaseModel):
    """Base schema for vendor data."""
    
    legal_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Registered legal name of the entity",
        example="Acme Private Limited",
    )
    
    trade_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Doing Business As (DBA) name if different",
        example="Acme Tech",
    )
    
    entity_type: Literal[
        "Private Limited",
        "Public Limited",
        "LLP",
        "Partnership",
        "Proprietorship",
        "HUF",
        "Other"
    ] = Field(
        ...,
        description="Legal entity type",
        example="Private Limited",
    )
    
    gstin: str = Field(
        ...,
        min_length=15,
        max_length=15,
        description="15-character Goods and Services Tax Identification Number",
        example="27AAAAA0000A1Z5",
    )
    
    pan_number: str = Field(
        ...,
        min_length=10,
        max_length=10,
        description="10-character Permanent Account Number",
        example="AAAAA0000A",
    )
    
    cin_number: Optional[str] = Field(
        None,
        max_length=21,
        description="Corporate Identification Number (for companies)",
        example="U72900MH2020PTC000000",
    )
    
    msme_registered: bool = Field(
        False,
        description="Whether the vendor is registered under MSME",
    )
    
    udyam_number: Optional[str] = Field(
        None,
        max_length=20,
        description="Udyam Registration Number for MSME",
        example="UDYAM-MH-00-0000000",
    )
    
    msme_type: Optional[Literal["MICRO", "SMALL", "MEDIUM"]] = Field(
        None,
        description="MSME Classification",
        example="SMALL",
    )
    
    contact_email: str = Field(
        ...,
        description="Primary contact email address",
        example="contact@acme.example.com",
    )
    
    contact_phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Primary contact phone number",
        example="+91-9876543210",
    )
    
    address: str = Field(
        ...,
        description="Registered business address",
        example="123 Tech Park, Mumbai, Maharashtra 400001",
    )

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, v: str) -> str:
        """Validate GSTIN format basically."""
        v = v.upper()
        if len(v) != 15:
            raise ValueError("GSTIN must be exactly 15 characters long")
        return v

    @field_validator("pan_number")
    @classmethod
    def validate_pan(cls, v: str) -> str:
        """Validate PAN format basically."""
        v = v.upper()
        if len(v) != 10:
            raise ValueError("PAN must be exactly 10 characters long")
        return v


class VendorCreate(VendorBase):
    """Schema for creating a new vendor."""
    pass


class VendorUpdate(BaseModel):
    """Schema for updating an existing vendor."""
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None
    entity_type: Optional[str] = None
    gstin: Optional[str] = None
    pan_number: Optional[str] = None
    cin_number: Optional[str] = None
    msme_registered: Optional[bool] = None
    udyam_number: Optional[str] = None
    msme_type: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    compliance_status: Optional[Literal["PENDING", "VERIFIED", "REJECTED"]] = None


class VendorResponse(VendorBase):
    """Schema for a vendor response including DB metadata."""
    id: int
    compliance_status: Literal["PENDING", "VERIFIED", "REJECTED"]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VendorListResponse(BaseModel):
    """Schema for a list of vendors."""
    vendors: list[VendorResponse]
    total: int
