import type { RadioChangeEvent } from 'antd';
import { Button, Flex, Form, Input, Pagination, Space, Table, Typography } from 'antd';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router';

import { TableQuickFilter } from '@/components/list/table-quick-filter/table-quick-filter';
import { useQuickFilter } from '@/hooks/use-quick-filter';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { getDataProductTableColumns } from '@/pages/data-products/components/data-products-table/data-products-table-columns.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import {
    useGetAllDataProductsQuery,
    useGetUserDataProductsQuery,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { DataProductsGetContract } from '@/types/data-product';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import { SearchForm } from '@/types/shared';
import { QuickFilterParticipation } from '@/types/shared/table-filters';

import styles from './data-products-table.module.scss';

function filterDataProducts(dataProducts: DataProductsGetContract, searchTerm?: string) {
    if (!searchTerm) {
        return dataProducts;
    }
    return dataProducts.filter((dataProduct) => dataProduct.name.toLowerCase().includes(searchTerm.toLowerCase()));
}

export function DataProductsTable() {
    const currentUser = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    const { quickFilter, onQuickFilterChange, quickFilterOptions } = useQuickFilter({});
    const navigate = useNavigate();
    const { data: dataProducts = [], isFetching } = useGetAllDataProductsQuery();
    const { data: userDataProducts = [], isFetching: isFetchingUserDataProducts } = useGetUserDataProductsQuery(
        currentUser?.id || '',
        { skip: !currentUser },
    );
    const { data: access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_DATAPRODUCT });
    const canCreateDataProduct = access?.allowed ?? false;
    const { pagination, handlePaginationChange, resetPagination } = useTablePagination({});
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDataProducts = useMemo(() => {
        const data = quickFilter === QuickFilterParticipation.Me ? userDataProducts : dataProducts;
        return filterDataProducts(data, searchTerm);
    }, [quickFilter, userDataProducts, dataProducts, searchTerm]);

    const columns = useMemo(
        () => getDataProductTableColumns({ t, dataProducts: filteredDataProducts }),
        [t, filteredDataProducts],
    );

    const handlePageChange = (page: number, pageSize: number) => {
        handlePaginationChange({
            ...pagination,
            current: page,
            pageSize,
        });
    };

    const navigateToDataProduct = (dataProductId: string) => {
        navigate(createDataProductIdPath(dataProductId));
    };

    const handleQuickFilterChange = ({ target: { value } }: RadioChangeEvent) => {
        onQuickFilterChange(value);
    };

    useEffect(() => {
        if (!isFetching && !isFetchingUserDataProducts) {
            resetPagination();
        }
    }, [filteredDataProducts, isFetching, isFetchingUserDataProducts, resetPagination]);

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Data Products')}</Typography.Title>
                <Form<SearchForm> form={searchForm} className={styles.searchForm}>
                    <Form.Item<SearchForm> name={'search'} initialValue={''} className={styles.formItem}>
                        <Input.Search placeholder={t('Search data products by name')} allowClear />
                    </Form.Item>
                </Form>
                <Space>
                    <Link to={ApplicationPaths.DataProductNew}>
                        <Button className={styles.formButton} type={'primary'} disabled={!canCreateDataProduct}>
                            {t('Create Data Product')}
                        </Button>
                    </Link>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Flex align="flex-end" justify="space-between" className={styles.tableBar}>
                    <TableQuickFilter
                        value={quickFilter}
                        onFilterChange={handleQuickFilterChange}
                        quickFilterOptions={quickFilterOptions}
                    />
                    <Pagination
                        current={pagination.current}
                        pageSize={pagination.pageSize}
                        total={filteredDataProducts.length}
                        onChange={handlePageChange}
                        size="small"
                        showTotal={(total, range) =>
                            t('Showing {{range0}}-{{range1}} of {{total}} data products', {
                                range0: range[0],
                                range1: range[1],
                                total: total,
                            })
                        }
                    />
                </Flex>

                <Table<DataProductsGetContract[0]>
                    onRow={(record) => ({
                        onClick: () => navigateToDataProduct(record.id),
                    })}
                    className={styles.table}
                    columns={columns}
                    dataSource={filteredDataProducts}
                    pagination={{
                        ...pagination,
                        position: [],
                    }}
                    rowKey={(record) => record.id}
                    loading={isFetching}
                    rowHoverable
                    rowClassName={styles.row}
                    size={'small'}
                />
            </Flex>
        </Flex>
    );
}
