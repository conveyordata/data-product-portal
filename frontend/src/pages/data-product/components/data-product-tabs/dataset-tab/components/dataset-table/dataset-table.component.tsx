import { Flex, Table, type TableColumnsType, type TableProps } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import type { DatasetLink } from '@/types/data-product';

import { getDataProductDatasetsColumns } from './dataset-table-columns.tsx';
import styles from './dataset-table.module.scss';

type Props = {
    dataProductId: string;
    datasets: DatasetLink[];
};
export function DatasetTable({ dataProductId, datasets }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);

    const { pagination, handlePaginationChange } = useTablePagination(datasets, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DatasetLink>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const columns: TableColumnsType<DatasetLink> = useMemo(() => {
        return getDataProductDatasetsColumns({
            t,
            datasetLinks: datasets,
        });
    }, [t, datasets]);

    if (!dataProduct) return null;

    return (
        <Flex className={styles.datasetListContainer}>
            <Table<DatasetLink>
                loading={isLoadingDataProduct}
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
