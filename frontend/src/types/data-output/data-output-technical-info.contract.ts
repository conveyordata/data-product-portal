import { DataOutputContract } from '@/types/data-output';
import { EnvironmentConfig } from '../environment';

export type TechnicalInfoContract = {
    environmentConfig: EnvironmentConfig;
    data_output: DataOutputContract;
};
