import { Flex, Typography } from 'antd';
// import { useTranslation } from 'react-i18next';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { GlueDataOutputContract, S3DataOutputContract } from '@/types/data-output';

type Props = {
    data_output_id: string;
};

export function DataOutputSubtitle({ data_output_id }: Props) {
    // const { t } = useTranslation();
    const { data: data_output } = useGetDataOutputByIdQuery(data_output_id);
    // TODO Better styling
    switch (data_output?.configuration_type) {
        case 'GlueDataOutput': {
            const glue_configuration = data_output.configuration as GlueDataOutputContract;
            return <Flex vertical>
                    <div>
                    <Typography.Text strong>Glue database: </Typography.Text>
                    <Typography.Text>{glue_configuration.glue_database}</Typography.Text>
                    </div>
                    <div>
                    <Typography.Text strong>Glue tables: </Typography.Text>
                    <Typography.Text>{glue_configuration.table_prefixes}</Typography.Text>
                    </div>
                </Flex>
            return <Typography.Text>Schema {glue_configuration.glue_database}</Typography.Text>;
        }
        case 'S3DataOutput': {
            const s3_configuration = data_output.configuration as S3DataOutputContract;
            return (
                <Flex vertical>
                    <div>
                    <Typography.Text strong>Bucket identifier: </Typography.Text>
                    <Typography.Text>{s3_configuration.bucket}</Typography.Text>
                    </div>
                    <div>
                    <Typography.Text strong>Full path: </Typography.Text>
                    <Typography.Text>{s3_configuration.bucket}/{s3_configuration.prefix}/*</Typography.Text>
                    </div>
                </Flex>
            );
        }
    }
}
