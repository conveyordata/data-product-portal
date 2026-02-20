import { DataOutputTechnicalInfo } from '@/components/data-outputs/data-output-technical-info/data-output-technical-info.component';

type Props = {
    dataProductId: string;
    technicalAssetId: string;
};

export function TechnologiesTab({ technicalAssetId, dataProductId }: Props) {
    return <DataOutputTechnicalInfo technicalAssetId={technicalAssetId} dataProductId={dataProductId} />;
}
