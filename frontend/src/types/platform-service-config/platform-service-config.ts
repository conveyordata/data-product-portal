import type { IdName } from '../shared';

export interface PlatformServiceConfigGetResponse {
    id: string;
    config: string[];
    platform: IdName;
    service: IdName;
}
