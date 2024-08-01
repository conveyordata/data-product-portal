export interface S3DataOutputContract {
    bucket: string;
    prefix: string;
    account_id: string;
    kms_key: string;
}

export interface S3DataOutputModel extends S3DataOutputContract {}
export type S3DataOutput = S3DataOutputContract;
