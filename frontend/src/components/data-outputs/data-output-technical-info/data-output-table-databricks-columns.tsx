import type { TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import type { DatabricksDataOutputContract } from '@/types/data-output';
import type { TechnicalInfoContract } from '@/types/data-output/data-output-technical-info.contract';

type Props = {
    t: TFunction;
};

export const getDatabricksTechnicalInformationColumns = ({ t }: Props): TableColumnsType<TechnicalInfoContract> => {
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
            title: t('Schema'),
            dataIndex: 'schema',
            render: (_, { data_output }) => {
                const configuration: DatabricksDataOutputContract =
                    data_output.configuration as DatabricksDataOutputContract;
                // TODO figure out how to use product aligned databases here and get their ARN?
                return configuration.schema;
            },
            width: '30%',
        },
    ];
};
