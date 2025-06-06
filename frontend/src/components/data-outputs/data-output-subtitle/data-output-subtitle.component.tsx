import { Flex, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useTranslation } from 'react-i18next';

import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import type { DataOutputContract } from '@/types/data-output';
import { DataOutputConfigurationTypes } from '@/types/data-output/data-output.contract';

type Props = {
    data_output_id: string;
};

function outputDescription(t: TFunction, data_output: DataOutputContract) {
    switch (data_output.configuration.configuration_type) {
        case DataOutputConfigurationTypes.S3DataOutput:
            return t('Glue database');
        case DataOutputConfigurationTypes.GlueDataOutput:
            return t('Glue database');
        case DataOutputConfigurationTypes.DatabricksDataOutput:
            return t('Databricks schema');
        case DataOutputConfigurationTypes.SnowflakeDataOutput:
            return t('Snowflake schema');
        case DataOutputConfigurationTypes.RedshiftDataOutput:
            return t('Redshift schema');
        default:
            return null;
    }
}

export function DataOutputSubtitle({ data_output_id }: Props) {
    const { t } = useTranslation();
    const { data: data_output } = useGetDataOutputByIdQuery(data_output_id);

    if (!data_output) {
        return null;
    }

    const description = outputDescription(t, data_output);

    if (!description) {
        return null;
    }

    return (
        <Flex vertical>
            <Typography.Text strong>{description}: </Typography.Text>
            <Typography.Text> {data_output.result_string} </Typography.Text>
        </Flex>
    );
}
