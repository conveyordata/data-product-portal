import { DataOutputConfiguration } from '.';

export interface DataOutputResultStringRequest {
    platform_id: string;
    service_id: string;
    configuration: DataOutputConfiguration;
}
