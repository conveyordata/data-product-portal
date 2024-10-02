import { Flex, Typography } from 'antd';
// import { useTranslation } from 'react-i18next';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { DatabricksDataOutputContract, GlueDataOutputContract, S3DataOutputContract } from '@/types/data-output';

type Props = {
    data_output_id: string;
};

export function DataOutputSubtitle({ data_output_id }: Props) {
    // const { t } = useTranslation();
    const { data: data_output } = useGetDataOutputByIdQuery(data_output_id);
    // TODO Better styling
    switch (data_output?.configuration.configuration_type) {
        case 'GlueDataOutput': {
            const glue_configuration = data_output.configuration as GlueDataOutputContract;
            return <Flex vertical>
                    <div>
                    <Typography.Text strong>Glue database: </Typography.Text>
                    <Typography.Text>{glue_configuration.database}</Typography.Text>
                    </div>
                </Flex>
        }
        case 'DatabricksDataOutput': {
            const databricks_configuration = data_output.configuration as DatabricksDataOutputContract;
            return <Flex vertical>
                    <div>
                    <Typography.Text strong>Databricks database: </Typography.Text>
                    <Typography.Text>{databricks_configuration.database}</Typography.Text>
                    </div>
                </Flex>
        }
        case 'S3DataOutput': {
            const s3_configuration = data_output.configuration as S3DataOutputContract;
            const configuration: S3DataOutputContract = data_output.configuration as S3DataOutputContract
            let suffix = '/' + configuration.suffix + '/'
            if (configuration.suffix === '') {
                suffix = '/'
            }
            return (
                <Flex vertical>
                    <div>
                    <Typography.Text strong>S3 Path: </Typography.Text>
                    <Typography.Text>{s3_configuration.bucket}{suffix}{s3_configuration.path}/*</Typography.Text>
                    </div>
                </Flex>
            );
        }
    }
}
