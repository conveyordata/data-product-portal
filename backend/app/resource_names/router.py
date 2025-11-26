from uuid import UUID

from app.resource_names.validation import NamespaceValidator


@router.get("/sanitize")
def get_data_product_namespace_suggestion(name: str) -> NamespaceSuggestion:
    return DataProductService.data_product_namespace_suggestion(name)


@router.get("/validate")
def validate_data_product_namespace(
    namespace: str, db: Session = Depends(get_db_session)
) -> NamespaceValidation:
    return NamespaceValidator(db).validate_namespace(namespace)


@router.get("/contraints")
def get_data_product_namespace_length_limits() -> NamespaceLengthLimits:
    return DataProductService.data_product_namespace_length_limits()espace, id)