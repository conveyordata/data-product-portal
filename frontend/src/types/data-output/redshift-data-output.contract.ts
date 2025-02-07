export interface RedshiftDataOutputContract {
    bucket: string;
    suffix: string;
    path: string;
    account_id: string;
    kms_key: string;
    configuration_type: string;
}

export interface RedshiftDataOutputModel extends RedshiftDataOutputContract {}
export type RedshiftDataOutput = RedshiftDataOutputContract;
