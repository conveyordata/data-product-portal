import { TechnicalAssetTechnicalInfo } from '@/components/technical-assets/technical-asset-technical-info/technical-asset-technical-info.component.tsx';

type Props = {
    dataProductId: string;
    technicalAssetId: string;
};

export function TechnologiesTab({ technicalAssetId, dataProductId }: Props) {
    return <TechnicalAssetTechnicalInfo technicalAssetId={technicalAssetId} dataProductId={dataProductId} />;
}
