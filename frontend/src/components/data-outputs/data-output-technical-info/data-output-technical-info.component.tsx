import { Table, type TableColumnsType } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import type { TechnicalInfoContract } from '@/types/data-output/data-output-technical-info.contract';
import { getTechnicalInformationColumns } from './data-output-table-columns';
import styles from './data-output-technical-info.module.scss';

type Props = {
    data_output_id: string;
};

export function DataOutputTechnicalInfo({ data_output_id }: Props) {
    const { t } = useTranslation();
    const { data: data_output, isLoading } = useGetDataOutputByIdQuery(data_output_id);
    const { data: { plugins: uiMetadataGroups } = {}, isLoading: isLoadingMetadata } = useGetPluginsQuery();
    const technicalInfo = data_output?.technical_info || [];
    const info_column =
        uiMetadataGroups?.find((plugin) => plugin.plugin === data_output?.configuration.configuration_type)
            ?.detailed_name ?? 'Info';

    const columns: TableColumnsType<TechnicalInfoContract> = useMemo(() => {
        return getTechnicalInformationColumns({
            t,
            info_column,
        });
    }, [t, info_column]);

    return (
        <Table<TechnicalInfoContract>
            loading={isLoading || isLoadingMetadata}
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
