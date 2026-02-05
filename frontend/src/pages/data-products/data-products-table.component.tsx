import { usePostHog } from '@posthog/react';
import { Button, Flex, type GetProps, type Input, Table } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router';
import { RoleFilter } from '@/components/filters/role-filter.component.tsx';
import SearchPage from '@/components/search-page/search-page.component.tsx';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { getDataProductTableColumns } from '@/pages/data-products/data-products-table-columns.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetAllDataProductsQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataProductsGetContract } from '@/types/data-product';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import styles from './data-products-table.module.scss';

type SearchProps = GetProps<typeof Input.Search>;

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
    const posthog = usePostHog();
    const navigate = useNavigate();
    const [selectedProductIds, setSelectedProductIds] = useState<string[]>([]);
    const [selectedRole, setSelectedRole] = useState<string | undefined>(undefined);

    const { data: dataProducts = [], isFetching } = useGetAllDataProductsQuery();
    const { data: access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_DATAPRODUCT });
    const canCreateDataProduct = access?.allowed ?? false;

    const [searchTerm, setSearchTerm] = useState<string>('');

    const onSearch: SearchProps['onChange'] = (e) => {
        setSearchTerm(e.target.value);
    };

    const filteredDataProducts = useMemo(() => {
        let filtered = filterDataProducts(dataProducts, searchTerm);
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

    const handleRoleChange = (selected: { productIds: string[]; role: string }) => {
        setSelectedProductIds(selected.productIds);
        setSelectedRole(selected.role);
    };

    return (
        <SearchPage
            onChange={onSearch}
            title={t('Data Products')}
            searchPlaceholder={t('Search Data Products by name')}
            actions={
                <Flex justify={'space-between'}>
                    <RoleFilter mode={'data_products'} selectedRole={selectedRole} onRoleChange={handleRoleChange} />
                    <Link
                        to={ApplicationPaths.DataProductNew}
                        onClick={() => posthog.capture(PosthogEvents.CREATE_DATA_PRODUCT_STARTED)}
                    >
                        <Button type={'primary'} disabled={!canCreateDataProduct}>
                            {t('Create Data Product')}
                        </Button>
                    </Link>
                </Flex>
            }
        >
            <Table<DataProductsGetContract[0]>
                onRow={(record) => ({
                    onClick: () => navigateToDataProduct(record.id),
                })}
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
                rowClassName={styles.row}
                size={'small'}
            />
        </SearchPage>
    );
}
