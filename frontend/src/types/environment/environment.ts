import { IdName } from '../shared';

export type Environment = IdName & {
    is_default: boolean;
};

export type EnvironmentCreateRequest = Omit<Environment, 'id'>;

export type EnvironmentCreateFormSchema = EnvironmentCreateRequest;
