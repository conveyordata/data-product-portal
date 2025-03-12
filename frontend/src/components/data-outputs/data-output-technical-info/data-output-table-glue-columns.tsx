import { TableColumnsType } from 'antd';
import { TFunction } from 'i18next';

import { GlueDataOutputContract } from '@/types/data-output';
import { TechnicalInfoContract } from '@/types/data-output/data-output-technical-info.contract';

type Props = {
    t: TFunction;
};

export const getGlueTechnicalInformationColumns = ({ t }: Props): TableColumnsType<TechnicalInfoContract> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Environment'),
            dataIndex: 'environment',
            render: (_, { environmentConfig }) => {
                return environmentConfig.environment.name;
            },
            width: '30%',
        },
        {
            title: t('Database'),
            dataIndex: 'database',
            render: (_, { data_output }) => {
                const configuration: GlueDataOutputContract = data_output.configuration as GlueDataOutputContract;
                // TODO figure out how to use product aligned databases here and get their ARN?
                return `${configuration.database}__${configuration.database_suffix}`;
            },
            width: '30%',
        },
    ];
};
