"""
Verification Schemas
Pydantic models for verification endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional


class SecurityAnswer(BaseModel):
    """Security question answer"""
    question: str = Field(..., description="The security question")
    answer: str = Field(..., description="User's answer to the security question")


class VerifyTransactionRequest(BaseModel):
    """Request to verify transaction with security questions"""
    transaction_id: int = Field(..., description="Transaction ID to verify")
    answers: dict[str, str] = Field(
        ...,
        description="Dictionary of {question: answer} for security questions"
    )


class VerifyTransactionResponse(BaseModel):
    """Response from verification request"""
    verified: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Verification result message")
    transaction_id: int = Field(..., description="Transaction ID")
    status: Optional[str] = Field(None, description="Transaction status after verification")


class VerificationEmailResponse(BaseModel):
    """Response from sending verification email"""
    sent: bool = Field(..., description="Whether email was sent successfully")
    message: str = Field(..., description="Status message")

