import { DataProductSettings } from '@/components/data-products/data-product-settings/data-product-settings.component';

type Props = {
    datasetId: string;
    dataProductId: string;
};

export function SettingsTab({ datasetId, dataProductId }: Props) {
    return <DataProductSettings id={datasetId} scope={'dataset'} dataProductId={dataProductId} />;
}
