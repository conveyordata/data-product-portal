import type { DataOutputContract } from '@/types/data-output';

import type { EnvironmentConfig } from '../environment';

export type TechnicalInfoContract = {
    environmentConfig: EnvironmentConfig;
    data_output: DataOutputContract;
};
