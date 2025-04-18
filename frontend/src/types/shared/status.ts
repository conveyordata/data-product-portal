import { DatasetStatus } from '@/types/dataset/dataset.contract.ts';

import { DataOutputStatus } from '../data-output';
import { DataProductStatus } from '../data-product';

export type Status = DataProductStatus | DatasetStatus | DataOutputStatus;
