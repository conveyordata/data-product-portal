import { usePostHog } from '@posthog/react';
import { Button, Flex, Input, Radio, type RadioChangeEvent, Table } from 'antd';
import { parseAsBoolean, parseAsString, useQueryState } from 'nuqs';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router';

import { RoleFilter } from '@/components/filters/role-filter.component.tsx';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { getDataProductTableColumns } from '@/pages/data-products/data-products-table-columns.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import {
    useGetAllDataProductsQuery,
    useGetUserDataProductsQuery,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataProductsGetContract } from '@/types/data-product';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import styles from './data-products-tab.module.scss';

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

export function DataProductsTab() {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);

    const [searchTerm, setSearchTerm] = useQueryState('dp-search', parseAsString.withDefault(''));
    const [showAllProducts, setShowAllProducts] = useQueryState('dp-showAll', parseAsBoolean.withDefault(false));
    const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
    const [selectedProductIds, setSelectedProductIds] = useState<string[]>([]);

    const { data: userDataProducts = [], isFetching: isFetchingUserProducts } = useGetUserDataProductsQuery(
        currentUser?.id ?? '',
        { skip: !currentUser || showAllProducts },
    );
    const { data: allDataProducts = [], isFetching: isFetchingAllProducts } = useGetAllDataProductsQuery(undefined, {
        skip: !showAllProducts,
    });

    const dataProducts = showAllProducts ? allDataProducts : userDataProducts;
    const isFetching = showAllProducts ? isFetchingAllProducts : isFetchingUserProducts;

    const { data: access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_DATAPRODUCT });
    const canCreateDataProduct = access?.allowed ?? false;

    const onSearch = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            setSearchTerm(e.target.value || null);
        },
        [setSearchTerm],
    );

    const filteredDataProducts = useMemo(() => {
        let filtered = filterDataProducts(dataProducts, searchTerm || undefined);
        filtered = filterDataProductsByRoles(filtered, selectedProductIds);
        return filtered;
    }, [dataProducts, searchTerm, selectedProductIds]);

    const columns = useMemo(
        () => getDataProductTableColumns({ t, dataProducts: filteredDataProducts }),
        [t, filteredDataProducts],
    );

    const navigateToDataProduct = (dataProductId: string) => {
        navigate(createDataProductIdPath(dataProductId));
    };

    const handleRoleChange = (selected: { productIds: string[]; roles: string[] }) => {
        setSelectedProductIds(selected.productIds);
        setSelectedRoles(selected.roles);
        // Switch to "My Data Products" when roles are selected
        if (selected.roles.length > 0) {
            setShowAllProducts(false);
        }
    };

    const handleShowAllChange = (e: RadioChangeEvent) => {
        setShowAllProducts(e.target.value || null);
        // Reset role filter when switching between views
        setSelectedProductIds([]);
        setSelectedRoles([]);
    };

    return (
        <Flex vertical gap="small">
            {/* Search and Actions */}
            <Flex justify="space-between" align="center">
                <Flex gap="middle" flex={1} align="center">
                    <Input.Search
                        placeholder={t('Search Data Products by name')}
                        value={searchTerm ?? ''}
                        onChange={onSearch}
                        allowClear
                        style={{ maxWidth: 400 }}
                    />
                    <Radio.Group value={showAllProducts} onChange={handleShowAllChange} optionType="button">
                        <Radio.Button value={false}>{t('My Data Products')}</Radio.Button>
                        <Radio.Button value={true}>{t('All Data Products')}</Radio.Button>
                    </Radio.Group>
                    <RoleFilter mode={'data_products'} selectedRoles={selectedRoles} onRoleChange={handleRoleChange} />
                </Flex>
                <Link
                    to={ApplicationPaths.DataProductNew}
                    onClick={() => posthog.capture(PosthogEvents.CREATE_DATA_PRODUCT_STARTED)}
                >
                    <Button type={'primary'} disabled={!canCreateDataProduct}>
                        {t('Create Data Product')}
                    </Button>
                </Link>
            </Flex>

            {/* Pending Requests Section */}

            {/* Table */}
            <Table<DataProductsGetContract[0]>
                onRow={(record) => ({
                    onClick: () => navigateToDataProduct(record.id),
                })}
                rowClassName={styles.row}
                columns={columns}
                dataSource={filteredDataProducts}
                pagination={{
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{count}} Data Products', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                }}
                rowKey={(record) => record.id}
                loading={isFetching}
                rowHoverable
                size={'small'}
            />
        </Flex>
    );
}
