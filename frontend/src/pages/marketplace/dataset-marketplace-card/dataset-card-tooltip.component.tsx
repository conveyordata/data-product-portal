import { Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';

import { DatasetProductList } from './dataset-product-list.component';

type Props = {
    dataset_id: string;
    number_of_data_products?: number;
};

export function DatasetCardTooltip({ dataset_id, number_of_data_products }: Props) {
    const { t } = useTranslation();

    return (
        <Tooltip
            placement="bottom"
            color="white"
            title={
                number_of_data_products && number_of_data_products > 0 ? (
                    <DatasetProductList dataset_id={dataset_id} />
                ) : null
            }
        >
            {t('{{count}} Data Products', { count: number_of_data_products })}
        </Tooltip>
    );
}
