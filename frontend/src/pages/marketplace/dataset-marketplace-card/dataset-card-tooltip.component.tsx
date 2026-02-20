import { Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';

import { DatasetProductList } from './dataset-product-list.component';

type Props = {
    outputPortId: string;
    dataProductId: string;
    number_of_data_products?: number;
};

export function DatasetCardTooltip({ outputPortId, dataProductId, number_of_data_products }: Props) {
    const { t } = useTranslation();

    return (
        <Tooltip
            placement="bottom"
            color="white"
            title={
                number_of_data_products && number_of_data_products > 0 ? (
                    <DatasetProductList outputPortId={outputPortId} dataProductId={dataProductId} />
                ) : null
            }
        >
            {t('{{count}} Data Products', { count: number_of_data_products })}
        </Tooltip>
    );
}
