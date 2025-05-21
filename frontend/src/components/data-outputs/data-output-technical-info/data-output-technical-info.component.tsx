import { Table, TableColumnsType } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { DataOutputConfigurationTypes } from '@/types/data-output/data-output.contract';
import { TechnicalInfoContract } from '@/types/data-output/data-output-technical-info.contract';

import { getTechnicalInformationColumns } from './data-output-table-columns';
import styles from './data-output-technical-info.module.scss';

type Props = {
    data_output_id: string;
};

export function DataOutputTechnicalInfo({ data_output_id }: Props) {
    const { t } = useTranslation();
    const { data: data_output, isLoading } = useGetDataOutputByIdQuery(data_output_id);
    const technicalInfo = data_output?.technical_info || [];

    const info_column = useMemo(() => {
        switch (data_output?.configuration.configuration_type) {
            case DataOutputConfigurationTypes.S3DataOutput:
                return 'Path';
            case DataOutputConfigurationTypes.GlueDataOutput:
                return 'Database';
            case DataOutputConfigurationTypes.DatabricksDataOutput:
                return 'Schema';
            case DataOutputConfigurationTypes.SnowflakeDataOutput:
                return 'Schema';
            case DataOutputConfigurationTypes.RedshiftDataOutput:
                return 'Schema';
            default:
                return 'Info';
        }
    }, [data_output]);

    const columns: TableColumnsType<TechnicalInfoContract> = useMemo(() => {
        return getTechnicalInformationColumns({
            t,
            info_column,
        });
    }, [t, info_column]);

    return (
        <Table<TechnicalInfoContract>
            loading={isLoading}
            className={styles.dataOutputListTable}
            columns={columns}
            dataSource={technicalInfo}
            rowKey={(info) => info.environment_id}
            pagination={false}
            rowClassName={styles.tableRow}
            size={'small'}
        />
    );
}
