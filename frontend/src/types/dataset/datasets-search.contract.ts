import type { DatasetsGetContractSingle } from '@/types/dataset/datasets-get.contract.ts';

export type DatasetsSearchContract = {
    datasets: (DatasetsGetContractSingle & {
        rank: number;
    })[];
    reasoning: string;
};
