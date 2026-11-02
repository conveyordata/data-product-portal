import type { TableColumnsType } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { TechnicalAssetOutlined } from '@/components/icons';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import {
    type TechnicalInfo,
    useGetTechnicalAssetQuery,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { useGetPluginsQuery } from '@/store/api/services/generated/pluginsApi';
import { getTechnicalInformationColumns } from './technical-asset-table-columns.tsx';
import styles from './technical-asset-technical-info.module.scss';

type Props = {
    technicalAssetId: string;
    dataProductId: string;
};

export function TechnicalAssetTechnicalInfo({ technicalAssetId, dataProductId }: Props) {
    const { t } = useTranslation();
    const technicalAssetQuery = useGetTechnicalAssetQuery({ id: technicalAssetId, dataProductId });
    const { data: technicalASset } = technicalAssetQuery;
    const { data: { plugins: uiMetadataGroups } = {}, isLoading: isLoadingMetadata } = useGetPluginsQuery();
    const technicalInfo = technicalASset?.technical_info || [];
    const info_column =
        uiMetadataGroups?.find((plugin) => plugin.plugin === technicalASset?.configuration.name)?.detailed_name ??
        'Info';

    const columns: TableColumnsType<TechnicalInfo> = useMemo(() => {
        return getTechnicalInformationColumns({
            t,
            info_column,
        });
    }, [t, info_column]);

    return (
        <ListTable<TechnicalInfo>
            query={technicalAssetQuery}
            dataSource={technicalInfo}
            columns={columns}
            subject={t('technical information')}
            emptyState={{
                icon: <TechnicalAssetOutlined />,
                title: t('No technical information yet'),
                description: t('Connection details appear here per environment once this asset is provisioned.'),
            }}
            loading={isLoadingMetadata}
            className={styles.dataOutputListTable}
            rowKey={(info) => info.environment_id}
            pagination={false}
            rowClassName={styles.tableRow}
            size="small"
        />
    );
}
