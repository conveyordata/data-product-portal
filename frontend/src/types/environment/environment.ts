import { IdName } from '../shared';

export type Environment = IdName & {
    is_default: boolean;
};
