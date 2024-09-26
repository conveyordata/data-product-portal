import { Flex, Table, TableColumnsType, Typography } from 'antd';
// import { useTranslation } from 'react-i18next';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { DataOutputContract, GlueDataOutputContract, S3DataOutputContract } from '@/types/data-output';
import styles from './data-output-technical-info.module.scss'
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetEnvironmentPlatformServiceConfigQuery } from '@/store/features/environments/environments-api-slice';
import { getS3TechnicalInformationColumns } from './data-output-table-s3-columns';
import { TechnicalInfoContract } from '@/types/data-output/data-output-technical-info.contract';
import { getGlueTechnicalInformationColumns } from './data-output-table-glue-columns';

type Props = {
    data_output_id: string;
};

export function DataOutputTechnicalInfo({ data_output_id }: Props) {
    const { t } = useTranslation();
    const { data: data_output, isLoading: isLoadingDataOutput } = useGetDataOutputByIdQuery(data_output_id);
    const { data: environmentConfig, isFetching: isLoadingConfig} = useGetEnvironmentPlatformServiceConfigQuery({
        platformId: data_output!.platform_id,
        serviceId: data_output!.service_id
    }, {
        skip: !data_output
    });
    const technicalInfo: TechnicalInfoContract[] = useMemo(() =>
            (environmentConfig ?? []).map((env) => {
                return {
                    environmentConfig: env,
                    data_output: data_output ?? {} as DataOutputContract
                }
            }
    ), [data_output, environmentConfig])

    const columns: TableColumnsType<TechnicalInfoContract> = useMemo(() => {
        switch (data_output?.configuration.configuration_type) {
            case 'S3DataOutput':
                return getS3TechnicalInformationColumns({t})
            case 'GlueDataOutput':
                return getGlueTechnicalInformationColumns({t})
            default:
                return []
        }
    }, [t, technicalInfo, data_output])

    return <Table<TechnicalInfoContract>
                loading={isLoadingDataOutput || isLoadingConfig}
                className={styles.dataOutputListTable}
                columns={columns}
                dataSource={technicalInfo}
                rowKey={({environmentConfig}) => environmentConfig.id}
                pagination={false}
                rowClassName={styles.tableRow}
                size={'small'}
            />
    // // TODO Better styling
    // switch (data_output?.configuration_type) {
    //     case 'GlueDataOutput': {
    //         const glue_configuration = data_output.configuration as GlueDataOutputContract;
    //         return <Flex vertical>
    //                 <div>
    //                 <Typography.Text strong>Glue database: </Typography.Text>
    //                 <Typography.Text>{glue_configuration.glue_database}</Typography.Text>
    //                 </div>
    //                 <div>
    //                 <Typography.Text strong>Glue tables: </Typography.Text>
    //                 <Typography.Text>{glue_configuration.table_prefixes}</Typography.Text>
    //                 </div>
    //             </Flex>
    //     }
    //     case 'S3DataOutput': {
    //         const s3_configuration = data_output.configuration as S3DataOutputContract;
    //         return (
    //             <Flex vertical>
    //                 <div>
    //                 <Typography.Text strong>Bucket identifier: </Typography.Text>
    //                 <Typography.Text>{s3_configuration.bucket}</Typography.Text>
    //                 </div>
    //                 <div>
    //                 <Typography.Text strong>Full path: </Typography.Text>
    //                 <Typography.Text>{s3_configuration.bucket}/{s3_configuration.prefix}/*</Typography.Text>
    //                 </div>
    //             </Flex>
    //         );
    //     }
    // }
}
