import type { TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import type { TechnicalInfo } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';

type Props = {
    t: TFunction;
    info_column: string;
};

export const getTechnicalInformationColumns = ({ t, info_column }: Props): TableColumnsType<TechnicalInfo> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'environment_id',
            hidden: true,
        },
        {
            title: t('Environment'),
            dataIndex: 'environment',
            width: '30%',
        },
        {
            title: t(info_column),
            dataIndex: 'info',
            width: '30%',
        },
    ];
};
