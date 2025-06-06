import type { IdName } from '../shared';

interface Config {
    identifiers: string[];
}

export interface PlatformServiceConfigCreateRequest {
    platformId: string;
    serviceId: string;
    config: Config;
}

export interface PlatformServiceConfigGetResponse {
    id: string;
    config: string[];
    platform: IdName;
    service: IdName;
}

export type PlatformServiceConfigContract = Omit<PlatformServiceConfigGetResponse, 'platform' | 'service'> & {
    platformName: string;
    serviceName: string;
};

export type PlatformServiceConfigCreateFormSchema = Omit<PlatformServiceConfigCreateRequest, 'config'> & {
    config: string;
};

export type PlatformServiceConfigMapping = {
    [key: string]: object;
};
