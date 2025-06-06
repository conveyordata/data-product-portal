import { Flex, Skeleton, Table, type TableColumnsType, type TableProps } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import type { DataOutputDatasetLink } from '@/types/data-output';

import { getDataOutputDatasetsColumns } from './dataset-table-columns.tsx';
import styles from './dataset-table.module.scss';

type Props = {
    dataProductId: string | undefined;
    dataOutputId: string;
    datasets: DataOutputDatasetLink[];
};
export function DatasetTable({ dataProductId, dataOutputId, datasets }: Props) {
    const { t } = useTranslation();
    const { data: dataOutput, isLoading: isLoadingDataOutput } = useGetDataOutputByIdQuery(dataOutputId);

    const { pagination, handlePaginationChange } = useTablePagination(datasets, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DataOutputDatasetLink>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const columns: TableColumnsType<DataOutputDatasetLink> = useMemo(() => {
        return getDataOutputDatasetsColumns({
            t,
            dataProductId,
        });
    }, [dataProductId, t]);

    if (!dataOutput) return <Skeleton />;

    return (
        <Flex className={styles.datasetListContainer}>
            <Table<DataOutputDatasetLink>
                loading={isLoadingDataOutput}
                className={styles.datasetListTable}
                columns={columns}
                dataSource={datasets}
                rowKey={({ id }) => id}
                onChange={onChange}
                pagination={{
                    ...pagination,
                    position: ['topRight'],
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{total}} datasets', {
                            range0: range[0],
                            range1: range[1],
                            total: total,
                        }),
                    className: styles.pagination,
                }}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
