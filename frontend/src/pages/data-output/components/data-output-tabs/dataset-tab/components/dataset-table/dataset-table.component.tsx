import { Flex, Skeleton, Table, type TableColumnsType, type TableProps } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import {
    type OutputPortLink,
    useGetTechnicalAssetQuery,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import styles from './dataset-table.module.scss';
import { getDataOutputDatasetsColumns } from './dataset-table-columns.tsx';

type Props = {
    dataProductId: string;
    dataOutputId: string;
    datasets: OutputPortLink[];
};
export function DatasetTable({ dataProductId, dataOutputId, datasets }: Props) {
    const { t } = useTranslation();
    const { data: dataOutput, isLoading: isLoadingDataOutput } = useGetTechnicalAssetQuery({
        id: dataOutputId,
        dataProductId,
    });

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

    if (!dataOutput) return <Skeleton />;

    return (
        <Flex className={styles.datasetListContainer}>
            <Table<OutputPortLink>
                loading={isLoadingDataOutput}
                className={styles.datasetListTable}
                columns={columns}
                dataSource={datasets}
                rowKey={({ id }) => id}
                onChange={onChange}
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
                size={'small'}
            />
        </Flex>
    );
}
