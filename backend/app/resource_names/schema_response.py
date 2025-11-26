from enum import Enum
from warnings import deprecated

from pydantic import BaseModel


@deprecated("Use ResourceNameValidationResult instead")
class NamespaceValidityType(str, Enum):
    VALID = "VALID"
    INVALID_LENGTH = "INVALID_LENGTH"
    INVALID_CHARACTERS = "INVALID_CHARACTERS"
    DUPLICATE_NAMESPACE = "DUPLICATE_NAMESPACE"


@deprecated("Use NamespaceValidityType instead")
class NamespaceValidation(BaseModel):
    validity: NamespaceValidityType

class ResourceNameValidationResult(str, Enum):
    VALID = "VALID"
    INVALID_LENGTH = "INVALID_LENGTH"
    INVALID_CHARACTERS = "INVALID_CHARACTERS"
    DUPLICATE_RESOURCE_NAME = "DUPLICATE_RESOURCE_NAME"

class ResourceNameValidationResponse(BaseModel):
    validity: ResourceNameValidationResult

@deprecated("Use ResourceNameSuggestion instead")
class NamespaceSuggestion(BaseModel):
    namespace: str


class ResourceNameSuggestion(BaseModel):
    resource_name: str

@deprecated("Use ResourceNameLimits instead")
class NamespaceLengthLimits(BaseModel):
    max_length: int

class ResourceNameLimits(BaseModel):
    max_length: int
