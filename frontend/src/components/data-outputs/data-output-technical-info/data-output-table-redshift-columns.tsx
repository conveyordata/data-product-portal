import type { TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';
import type { TechnicalInfoContract } from '@/types/data-output/data-output-technical-info.contract';
import type { RedshiftDataOutputContract } from '@/types/data-output';

type Props = {
    t: TFunction;
};

export const getRedshiftTechnicalInformationColumns = ({ t }: Props): TableColumnsType<TechnicalInfoContract> => {
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
                const configuration: RedshiftDataOutputContract =
                    data_output.configuration as RedshiftDataOutputContract;
                // TODO figure out how to use product aligned databases here and get their ARN?
                return `${configuration.database}__${configuration.schema}.${configuration.table}`;
            },
            width: '30%',
        },
    ];
};
