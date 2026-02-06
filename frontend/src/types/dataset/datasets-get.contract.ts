import type { DataQualityStatus } from '@/store/api/services/generated/outputPortDataQualityApi';
import type { DatasetContract } from '@/types/dataset';
import type { TagContract } from '@/types/tag';

export type DatasetsGetContractSingle = Omit<DatasetContract, 'data_product_links' | 'owners' | 'tags'> & {
    data_product_count: number;
    quality_status?: DataQualityStatus;
    tags: Omit<TagContract, 'id'>[];
    rolled_up_tags: Omit<TagContract, 'id'>[];
    data_product_name: string;
};

export type DatasetsGetContract = DatasetsGetContractSingle[];
