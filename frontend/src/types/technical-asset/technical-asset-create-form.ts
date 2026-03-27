import type {
    TechnicalAssetStatus,
    TechnicalMapping,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
export type TechnicalAssetConfiguration = Record<string, unknown> & {
    configuration_type: string;
};

export type TechnicalAssetsCreateForm = {
    name: string;
    namespace: string;
    tag_ids: string[];
    platform_id: string;
    service_id: string;
    status: TechnicalAssetStatus;
    description: string;
    configuration: TechnicalAssetConfiguration;
    technical_mapping: TechnicalMapping;
};
