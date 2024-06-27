import { DataProductContract } from '../data-product';

export interface PermissionSetContract {
    id: string;
    dataProduct: DataProductContract;
    environment: string;
    name: string;
    roleArn: string;
}

export interface PermissionSetModel extends PermissionSetContract {}
