import { useTranslation } from 'react-i18next';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetOutputPortQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

type Props = {
    dataProductId?: string;
    datasetId?: string;
};

export function UsageTab({ dataProductId, datasetId }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct } = useGetDataProductQuery(dataProductId ?? '', { skip: !dataProductId });
    const { data: dataset } = useGetOutputPortQuery(
        { dataProductId: dataProductId ?? '', id: datasetId ?? '' },
        { skip: !datasetId || !dataProductId },
    );

    const content = dataProduct?.usage ?? dataset?.usage;

    return <TextEditor isDisabled={true} initialContent={content ?? t('Not available')} />;
}
