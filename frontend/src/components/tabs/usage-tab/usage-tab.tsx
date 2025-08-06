import { useTranslation } from 'react-i18next';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';

type Props = {
    dataProductId?: string;
    datasetId?: string;
};

export function UsageTab({ dataProductId, datasetId }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId ?? '', { skip: !dataProductId });
    const { data: dataset } = useGetDatasetByIdQuery(datasetId ?? '', { skip: !datasetId });

    const content = dataProduct?.usage ?? dataset?.usage;

    return <TextEditor isDisabled={true} initialContent={content ?? t('Not available')} />;
}
