import { Flex, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

// import { useTranslation } from 'react-i18next';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import {
    DatabricksDataOutputContract,
    GlueDataOutputContract,
    RedshiftDataOutputContract,
    S3DataOutputContract,
    SnowflakeDataOutputContract,
} from '@/types/data-output';

type Props = {
    data_output_id: string;
};

export function DataOutputSubtitle({ data_output_id }: Props) {
    const { t } = useTranslation();
    const { data: data_output } = useGetDataOutputByIdQuery(data_output_id);
    switch (data_output?.configuration.configuration_type) {
        case 'GlueDataOutput': {
            const glue_configuration = data_output.configuration as GlueDataOutputContract;
            return (
                <Flex vertical>
                    <div>
                        <Typography.Text strong>{t('Glue database')}: </Typography.Text>
                        <Typography.Text>
                            {glue_configuration.database}__{glue_configuration.database_suffix}
                        </Typography.Text>
                    </div>
                </Flex>
            );
        }
        case 'SnowflakeDataOutput': {
            const snowflake_configuration = data_output.configuration as SnowflakeDataOutputContract;
            return (
                <Flex vertical>
                    <div>
                        <Typography.Text strong>{t('Snowflake schema')}: </Typography.Text>
                        <Typography.Text>
                            {snowflake_configuration.database}__{snowflake_configuration.schema}
                        </Typography.Text>
                    </div>
                </Flex>
            );
        }
        case 'DatabricksDataOutput': {
            const databricks_configuration = data_output.configuration as DatabricksDataOutputContract;
            return (
                <Flex vertical>
                    <div>
                        <Typography.Text strong>{t('Databricks schema')}: </Typography.Text>
                        <Typography.Text>{databricks_configuration.schema}</Typography.Text>
                    </div>
                </Flex>
            );
        }
        case 'S3DataOutput': {
            const s3_configuration = data_output.configuration as S3DataOutputContract;
            const configuration: S3DataOutputContract = data_output.configuration as S3DataOutputContract;
            let suffix = '/' + configuration.suffix + '/';
            if (configuration.suffix === '') {
                suffix = '/';
            }
            return (
                <Flex vertical>
                    <div>
                        <Typography.Text strong>{t('S3 path')}: </Typography.Text>
                        <Typography.Text>
                            {s3_configuration.bucket}
                            {suffix}
                            {s3_configuration.path}/*
                        </Typography.Text>
                    </div>
                </Flex>
            );
        }
        case 'RedshiftDataOutput': {
            const redshift_configuration = data_output.configuration as RedshiftDataOutputContract;
            return (
                <Flex vertical>
                    <div>
                        <Typography.Text strong>{t('Redshift schema')}: </Typography.Text>
                        <Typography.Text>
                            {redshift_configuration.database}__{redshift_configuration.schema}.
                            {redshift_configuration.table}
                        </Typography.Text>
                    </div>
                </Flex>
            );
        }
    }
}
