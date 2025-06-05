import type { IdName } from '../shared';

export interface EnvironmentConfig {
    id: string;
    config: AWSS3Config[];
    platform: IdName;
    service: IdName;
    environment: IdName;
}

interface AWSS3Config {
    account_id: number;
    identifier: string;
    bucket_name: string;
    bucket_arn: string;
    kms_key_arn: string;
}

interface Config {
    [key: string]: AWSS3Config;
}

export type EnvironmentConfigContract = Omit<EnvironmentConfig, 'platform' | 'service'> & {
    platformName: string;
    serviceName: string;
};

export interface EnvironmentConfigCreateRequest {
    platform_id: string;
    service_id: string;
    config: Config;
}

export interface EnvironmentConfigCreateFormSchema {
    platformId: string;
    serviceId: string;
    config: string;
    identifiers: string;
}
