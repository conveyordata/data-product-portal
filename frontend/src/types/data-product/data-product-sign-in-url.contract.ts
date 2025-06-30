export interface DataProductGetSignInUrlRequest {
    id: string;
    environment: string;
    integration_type: string;
}

export type DataProductGetSignInUrlResponse = string;
