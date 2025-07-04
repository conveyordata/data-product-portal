import type { DatasetStatus } from '@/types/dataset/dataset.contract.ts';

import type { DataOutputStatus } from '../data-output';
import type { DataProductStatus } from '../data-product';

export type Status = DataProductStatus | DatasetStatus | DataOutputStatus;
