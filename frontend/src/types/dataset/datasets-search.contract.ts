import type { DatasetsGetContractSingle } from '@/types/dataset/datasets-get.contract.ts';

export type DatasetsSearchContract = (DatasetsGetContractSingle & {
    rank: number;
})[];
