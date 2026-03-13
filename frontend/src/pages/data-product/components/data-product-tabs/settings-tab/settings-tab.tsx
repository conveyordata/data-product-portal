import { DataProductSettings } from '@/components/data-products/data-product-settings/data-product-settings.component';

type Props = {
    dataProductId: string;
};

export function SettingsTab({ dataProductId }: Props) {
    return <DataProductSettings id={dataProductId} scope={'dataproduct'} />;
}
