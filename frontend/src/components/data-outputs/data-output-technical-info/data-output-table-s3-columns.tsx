import { TableColumnsType } from 'antd';
import { TFunction } from 'i18next';
import { TechnicalInfoContract } from '@/types/data-output/data-output-technical-info.contract';
import { S3DataOutputContract } from '@/types/data-output';

type Props = {
    t: TFunction;
};

export const getS3TechnicalInformationColumns = ({ t }: Props): TableColumnsType<TechnicalInfoContract> => {
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
            title: t('Path'),
            dataIndex: 'path',
            render: (_, { environmentConfig, data_output }) => {
                const configuration: S3DataOutputContract = data_output.configuration as S3DataOutputContract;
                const bucket_arn = environmentConfig.config.filter(
                    ({ identifier }) => identifier == configuration.bucket,
                )[0].bucket_arn;
                let suffix = '/' + configuration.suffix + '/';
                if (configuration.suffix === '') {
                    suffix = '/';
                }

                return bucket_arn + suffix + configuration.path + '/*';
            },
            width: '30%',
        },
    ];
};
