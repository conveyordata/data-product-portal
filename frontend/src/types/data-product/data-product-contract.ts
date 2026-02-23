import type { DataProductLifeCycle } from '@/store/api/services/generated/dataProductsApi.ts';
import type { DataProductType } from '@/store/api/services/generated/usersNotificationsApi.ts';
import type { DataOutputsGetContract } from '@/types/data-output/data-output-get.contract.ts';
import type { DatasetLink } from '@/types/data-product/dataset-link.contract.ts';
import type { DomainContract } from '@/types/domain';
import type { TagContract } from '@/types/tag';
import type { DataProductSettingValueContract } from '../data-product-setting';
import type { DatasetsGetContract } from '../dataset';

export enum DataProductStatus {
    Pending = 'pending',
    Active = 'active',
    Deleted = 'deleted',
}

export interface DataProductContract {
    id: string;
    name: string;
    description: string;
    about: string;
    type: DataProductType;
    type_id: string;
    status: DataProductStatus;
    lifecycle: DataProductLifeCycle;
    lifecycle_id: string;
    dataset_links: DatasetLink[];
    tag_ids: string[];
    tags: TagContract[];
    rolled_up_tags: TagContract[];
    domain: DomainContract;
    domain_id: string;
    namespace: string;
    usage?: string;
    data_outputs: DataOutputsGetContract;
    datasets: DatasetsGetContract;
    data_product_settings: DataProductSettingValueContract[];
}

export interface DataProductModel extends DataProductContract {}
