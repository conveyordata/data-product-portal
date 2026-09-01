import { ToolOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Button, Empty, Flex, Input, Radio, type RadioChangeEvent, Table } from 'antd';
import Paragraph from 'antd/es/typography/Paragraph';
import { parseAsString, parseAsStringEnum, useQueryState } from 'nuqs';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router';
import { RoleFilter } from '@/components/filters/role-filter.component.tsx';
import { PosthogEvents } from '@/constants/posthog.constants.ts';
import { getDataProductTableColumns } from '@/pages/product-studio/components/data-products-tab/data-products-table-columns.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    AssignmentFilter,
    type GetDataProductsResponseItem,
    useGetDataProductsQuery,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import styles from './data-products-tab.module.scss';

function filterDataProducts(dataProducts: GetDataProductsResponseItem[], searchTerm?: string) {
    if (!searchTerm) {
        return dataProducts;
    }
    return dataProducts.filter((dataProduct) => dataProduct.name.toLowerCase().includes(searchTerm.toLowerCase()));
}

function filterDataProductsByRoles(dataProducts: GetDataProductsResponseItem[], selectedProductIds: string[]) {
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
    const [assignmentFilter, setAssignmentFilter] = useQueryState(
        'dp-assignmentFilter',
        parseAsStringEnum<AssignmentFilter>(Object.values(AssignmentFilter)).withDefault(AssignmentFilter.OnlyAssigned),
    );
    const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
    const [selectedProductIds, setSelectedProductIds] = useState<string[]>([]);

    const { data: { data_products: dataProducts = [] } = {}, isFetching } = useGetDataProductsQuery(assignmentFilter, {
        skip: !currentUser,
    });

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
    };

    const handleShowAllChange = (e: RadioChangeEvent) => {
        setAssignmentFilter(e.target.value);
        // Reset role filter when switching between views
        setSelectedProductIds([]);
        setSelectedRoles([]);
    };
    const createButton = (
        <Link
            to={ApplicationPaths.DataProductNew}
            onClick={() => posthog.capture(PosthogEvents.CREATE_DATA_PRODUCT_STARTED)}
        >
            <Button type="primary" disabled={!canCreateDataProduct}>
                {t('Create Data Product')}
            </Button>
        </Link>
    );

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
                    <Radio.Group value={assignmentFilter} onChange={handleShowAllChange} optionType="button">
                        <Radio.Button value={AssignmentFilter.OnlyAssigned}>{t('My Data Products')}</Radio.Button>
                        <Radio.Button value={AssignmentFilter.All}>{t('All Data Products')}</Radio.Button>
                    </Radio.Group>
                    {assignmentFilter === AssignmentFilter.OnlyAssigned && (
                        <RoleFilter
                            mode="data_products"
                            selectedRoles={selectedRoles}
                            onRoleChange={handleRoleChange}
                        />
                    )}
                </Flex>
                {filteredDataProducts.length > 0 && createButton}
            </Flex>

            {/* Table */}
            <Table<GetDataProductsResponseItem>
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
                size="small"
                locale={{
                    emptyText: (
                        <Empty
                            styles={{ image: { height: 50 } }}
                            image={<ToolOutlined style={{ fontSize: 50 }} />}
                            description={
                                <>
                                    <Paragraph style={{ marginTop: 0, opacity: 0.45 }}>
                                        {t('Ready to build your first Data Product?')}
                                    </Paragraph>
                                    <Paragraph style={{ opacity: 0.45 }}>
                                        {t(
                                            "It looks like you don't have any Data Products yet. Create one to start managing your data assets.",
                                        )}
                                    </Paragraph>
                                    {createButton}
                                </>
                            }
                        />
                    ),
                }}
            />
        </Flex>
    );
}
