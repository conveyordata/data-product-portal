import { Table, TableColumnsType } from 'antd';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { DataOutputContract } from '@/types/data-output';
import styles from './data-output-technical-info.module.scss';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetEnvironmentPlatformServiceConfigQuery } from '@/store/features/environments/environments-api-slice';
import { getS3TechnicalInformationColumns } from './data-output-table-s3-columns';
import { TechnicalInfoContract } from '@/types/data-output/data-output-technical-info.contract';
import { getGlueTechnicalInformationColumns } from './data-output-table-glue-columns';
import { getDatabricksTechnicalInformationColumns } from './data-output-table-databricks-columns';
import { getSnowflakeTechnicalInformationColumns } from './data-output-table-snowflake-columns';

type Props = {
    data_output_id: string;
};

export function DataOutputTechnicalInfo({ data_output_id }: Props) {
    const { t } = useTranslation();
    const { data: data_output, isLoading: isLoadingDataOutput } = useGetDataOutputByIdQuery(data_output_id);
    const { data: environmentConfig, isFetching: isLoadingConfig } = useGetEnvironmentPlatformServiceConfigQuery(
        {
            platformId: data_output!.platform_id,
            serviceId: data_output!.service_id,
        },
        {
            skip: !data_output,
        },
    );
    const technicalInfo: TechnicalInfoContract[] = useMemo(
        () =>
            (environmentConfig ?? []).map((env) => {
                return {
                    environmentConfig: env,
                    data_output: data_output ?? ({} as DataOutputContract),
                };
            }),
        [data_output, environmentConfig],
    );

    const columns: TableColumnsType<TechnicalInfoContract> = useMemo(() => {
        switch (data_output?.configuration.configuration_type) {
            case 'S3DataOutput':
                return getS3TechnicalInformationColumns({ t });
            case 'GlueDataOutput':
                return getGlueTechnicalInformationColumns({ t });
            case 'DatabricksDataOutput':
                return getDatabricksTechnicalInformationColumns({ t });
            case 'SnowflakeDataOutput':
                return getSnowflakeTechnicalInformationColumns({ t });
            default:
                return [];
        }
    }, [t, data_output]);

    return (
        <Table<TechnicalInfoContract>
            loading={isLoadingDataOutput || isLoadingConfig}
            className={styles.dataOutputListTable}
            columns={columns}
            dataSource={technicalInfo}
            rowKey={({ environmentConfig }) => environmentConfig.id}
            pagination={false}
            rowClassName={styles.tableRow}
            size={'small'}
        />
    );
}
