import { DataOutputStatus } from '../data-output';
import { DataProductStatus } from '../data-product';
import { DatasetStatus } from '@/types/dataset/dataset.contract.ts';

export type Status = DataProductStatus | DatasetStatus | DataOutputStatus;
