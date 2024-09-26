import { IdName } from '../shared';

export interface EnvironmentConfig {
    id: string;
    config: Config[];
    platform: IdName;
    service: IdName;
    environment: IdName;
}

interface AWSS3Config {
    identifier: string;
    bucket_name: string;
    kms_key: string;
    is_default: boolean;
}

interface AWSGlueConfig {
    identifier: string;
    database_name: string;
    bucket_identifier: string;
    s3_path: string;
}

type Config = AWSS3Config | AWSGlueConfig;
