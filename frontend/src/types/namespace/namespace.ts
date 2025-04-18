export enum ValidationType {
    VALID = 'VALID',
    INVALID_LENGTH = 'INVALID_LENGTH',
    INVALID_CHARACTERS = 'INVALID_CHARACTERS',
    DUPLICATE_NAMESPACE = 'DUPLICATE_NAMESPACE',
}

export interface NamespaceValidationResponse {
    validity: ValidationType;
}

export interface NamespaceSuggestionResponse {
    namespace: string;
}

export interface NamespaceLengthLimitsResponse {
    max_length: number;
}
