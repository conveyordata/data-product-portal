import { useTranslation } from 'react-i18next';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';

type Props = {
    dataProductId: string;
};

export function UsageTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId, { skip: !dataProductId });

    return <TextEditor initialContent={dataProduct?.usage ?? t('Not available')} />;
}
