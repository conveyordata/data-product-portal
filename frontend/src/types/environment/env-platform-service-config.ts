import { IdName } from '../shared';

export interface EnvironmentConfig {
    id: string;
    config: Config;
    platform: IdName;
    service: IdName;
    environment: IdName;
}

interface AWSS3Config {
    account_id: number;
    name: string;
    arn: string;
    kms: string;
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
