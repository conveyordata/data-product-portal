import type { DataOutputContract } from '@/types/data-output';

export type DataOutputsGetContract = (DataOutputContract & {
    owner_id: string;
})[];
