import { Table, type TableColumnsType } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import {
    type TechnicalInfo,
    useGetTechnicalAssetQuery,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi';
import { getTechnicalInformationColumns } from './data-output-table-columns';
import styles from './data-output-technical-info.module.scss';

type Props = {
    technicalAssetId: string;
    dataProductId: string;
};

export function DataOutputTechnicalInfo({ technicalAssetId, dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: technicalASset, isLoading } = useGetTechnicalAssetQuery({ id: technicalAssetId, dataProductId });
    const { data: { plugins: uiMetadataGroups } = {}, isLoading: isLoadingMetadata } = useGetPluginsQuery();
    const technicalInfo = technicalASset?.technical_info || [];
    const info_column =
        uiMetadataGroups?.find((plugin) => plugin.plugin === technicalASset?.configuration.configuration_type)
            ?.detailed_name ?? 'Info';

    const columns: TableColumnsType<TechnicalInfo> = useMemo(() => {
        return getTechnicalInformationColumns({
            t,
            info_column,
        });
    }, [t, info_column]);

    return (
        <Table<TechnicalInfo>
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
