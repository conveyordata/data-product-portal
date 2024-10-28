import { TableColumnsType } from 'antd';
import { TFunction } from 'i18next';
import { TechnicalInfoContract } from '@/types/data-output/data-output-technical-info.contract';
import { SnowflakeDataOutputContract } from '@/types/data-output';

type Props = {
    t: TFunction;
};

export const getSnowflakeTechnicalInformationColumns = ({
    t,
}: Props): TableColumnsType<TechnicalInfoContract> => {
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
                return environmentConfig.environment.name
            },
            width: '30%',
        },
        {
            title: t('Schema'),
            dataIndex: 'schema',
            render: (_, { data_output }) => {
                const configuration: SnowflakeDataOutputContract = data_output.configuration as SnowflakeDataOutputContract
                // TODO figure out how to use product aligned databases here and get their ARN?
                return configuration.schema
            },
            width: '30%',
        },
    ];
};
