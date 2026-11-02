import { Flex, Skeleton, type TableColumnsType, type TableProps } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { type EmptyStateFilter, hasFailed } from '@/components/empty-state/empty-state.component.tsx';
import { OutputPortOutlined } from '@/components/icons';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import {
    type OutputPortLink,
    useGetTechnicalAssetQuery,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import styles from './output-port-table.module.scss';
import { getDataOutputDatasetsColumns } from './output-port-table-columns.tsx';

type Props = {
    dataProductId: string;
    dataOutputId: string;
    datasets: OutputPortLink[];
    filter?: EmptyStateFilter;
};
export function DatasetTable({ dataProductId, dataOutputId, datasets, filter }: Props) {
    const { t } = useTranslation();
    const technicalAssetQuery = useGetTechnicalAssetQuery({
        id: dataOutputId,
        dataProductId,
    });
    const { data: dataOutput } = technicalAssetQuery;

    const { pagination, handlePaginationChange } = useTablePagination(datasets, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<OutputPortLink>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const columns: TableColumnsType<OutputPortLink> = useMemo(() => {
        return getDataOutputDatasetsColumns({
            t,
            dataProductId,
        });
    }, [dataProductId, t]);

    if (!dataOutput && !hasFailed(technicalAssetQuery)) return <Skeleton />;

    return (
        <Flex className={styles.datasetListContainer}>
            <ListTable<OutputPortLink>
                query={technicalAssetQuery}
                dataSource={datasets}
                columns={columns}
                subject={t('Output Ports')}
                emptyState={{
                    icon: <OutputPortOutlined />,
                    title: t('No Output Ports yet'),
                    description: t('Link this Technical Asset to an Output Port to share its data.'),
                }}
                onChange={onChange}
                filter={filter}
                className={styles.datasetListTable}
                rowKey={({ id }) => id}
                pagination={{
                    ...pagination,
                    placement: ['topEnd'],
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{count}} Output Ports', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                    className: styles.pagination,
                }}
                rowClassName={styles.tableRow}
                size="small"
            />
        </Flex>
    );
}
