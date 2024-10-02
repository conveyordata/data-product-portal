export interface S3DataOutputContract {
    bucket: string;
    suffix: string;
    path: string;
    account_id: string;
    kms_key: string;
    configuration_type: string;
}

export interface S3DataOutputModel extends S3DataOutputContract {}
export type S3DataOutput = S3DataOutputContract;
