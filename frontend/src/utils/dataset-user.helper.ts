import { DatasetContract } from '@/types/dataset';

export function getIsDatasetOwner(dataset: DatasetContract, userId: string) {
    return dataset?.owners?.some((owner) => owner.id === userId);
}

export function getDatasetOwnerIds(dataset: DatasetContract) {
    return dataset.owners.map((owner) => owner.id);
}
