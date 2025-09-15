import { Button, Flex, Form, Input, Pagination, Space, Table, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router';
import { RoleFilter } from '@/components/filters/role-filter.component';
import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { getDataProductTableColumns } from '@/pages/data-products/components/data-products-table/data-products-table-columns.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetAllDataProductsQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import type { DataProductsGetContract } from '@/types/data-product';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import type { SearchForm } from '@/types/shared';
import styles from './data-products-table.module.scss';

function filterDataProducts(dataProducts: DataProductsGetContract, searchTerm?: string) {
    if (!searchTerm) {
        return dataProducts;
    }
    return dataProducts.filter((dataProduct) => dataProduct.name.toLowerCase().includes(searchTerm.toLowerCase()));
}

function filterDataProductsByRoles(dataProducts: DataProductsGetContract, selectedProductIds: string[]) {
    if (!selectedProductIds.length) {
        return dataProducts;
    }

    return dataProducts.filter((dataProduct) => {
        return selectedProductIds.includes(dataProduct.id);
    });
}

export function DataProductsTable() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [selectedProductIds, setSelectedProductIds] = useState<string[]>([]);
    const [selectedRole, setSelectedRole] = useState<string>('');

    const { data: dataProducts = [], isFetching } = useGetAllDataProductsQuery();
    const { data: access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_DATAPRODUCT });
    const canCreateDataProduct = access?.allowed ?? false;

    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDataProducts = useMemo(() => {
        let filtered = filterDataProducts(dataProducts, searchTerm);
        filtered = filterDataProductsByRoles(filtered, selectedProductIds);
        return filtered;
    }, [dataProducts, searchTerm, selectedProductIds]);

    const { pagination, handlePaginationChange } = useTablePagination(filteredDataProducts);

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

    const handleRoleChange = (selected: { productIds: string[]; role: string }) => {
        setSelectedProductIds(selected.productIds);
        setSelectedRole(selected.role);
    };

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
                    <Link
                        to={ApplicationPaths.DataProductNew}
                        onClick={() => posthog.capture(PosthogEvents.CREATE_DATA_PRODUCT_STARTED)}
                    >
                        <Button className={styles.formButton} type={'primary'} disabled={!canCreateDataProduct}>
                            {t('Create Data Product')}
                        </Button>
                    </Link>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Flex align="flex-end" justify="space-between" className={styles.tableBar}>
                    <RoleFilter mode={'data_products'} selectedRole={selectedRole} onRoleChange={handleRoleChange} />
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
