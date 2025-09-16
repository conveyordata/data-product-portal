import { Select, Space, Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useGetDataProductRoleAssignmentsQuery } from '@/store/features/role-assignments/data-product-roles-api-slice';
import { useGetDatasetRoleAssignmentsQuery } from '@/store/features/role-assignments/dataset-roles-api-slice';
import type { DataProductRoleAssignmentContract, DatasetRoleAssignmentContract } from '@/types/roles/role.contract';

interface RoleFilterProps {
    selectedRole: string | undefined;
    onRoleChange: (selected: { productIds: string[]; role: string }) => void;
    mode: 'data_products' | 'datasets';
}

export function RoleFilter({ selectedRole, onRoleChange, mode }: RoleFilterProps) {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser);
    const { data: userDatasetRoles = [] } = useGetDatasetRoleAssignmentsQuery(
        { user_id: currentUser?.id || '' },
        { skip: !currentUser || mode !== 'datasets' },
    );
    const { data: userDataProductRoles = [] } = useGetDataProductRoleAssignmentsQuery(
        { user_id: currentUser?.id || '' },
        { skip: !currentUser || mode !== 'data_products' },
    );

    // Get unique roles that the current user has across all data products
    const uniqueUserRoles = useMemo(() => {
        const userRoles = mode === 'data_products' ? userDataProductRoles : userDatasetRoles;
        if (!userRoles.length) return [];

        const uniqueRoles = new Map<string, { label: string; value: string; productIds: string[] }>();

        const get_id = (assignment: DataProductRoleAssignmentContract | DatasetRoleAssignmentContract): string => {
            if (mode === 'data_products') {
                return (assignment as DataProductRoleAssignmentContract).data_product.id;
            }
            if (mode === 'datasets') {
                return (assignment as DatasetRoleAssignmentContract).dataset.id;
            }
            throw new Error('Invalid assignment type for mode');
        };

        userRoles.forEach((assignment) => {
            const roleId = assignment.role.id;
            const productId = get_id(assignment);
            const roleName = assignment.role.name;
            if (!uniqueRoles.has(roleId)) {
                uniqueRoles.set(roleId, { label: roleName, value: roleId, productIds: [productId] });
            } else {
                uniqueRoles.get(roleId)?.productIds.push(productId);
            }
        });

        return Array.from(uniqueRoles.values()).sort((a, b) => a.label.localeCompare(b.label));
    }, [userDataProductRoles, userDatasetRoles, mode]);

    const handleRoleFilterChange = (roleId: string) => {
        const selectedRoleData = uniqueUserRoles.find((role) => role.value === roleId);
        const productIds = selectedRoleData ? selectedRoleData.productIds : [];
        onRoleChange({ productIds: productIds, role: selectedRoleData?.value || '' });
        const event =
            mode === 'data_products' ? PosthogEvents.DATA_PRODUCTS_FILTER_USED : PosthogEvents.MARKETPLACE_FILTER_USED;
        posthog.capture(event, {
            filter_type: 'roles',
            filter_value: roleId,
        });
    };

    if (uniqueUserRoles.length === 0) {
        return null;
    }

    return (
        <Space>
            <Typography.Text>
                {t(
                    mode === 'data_products'
                        ? 'Show only data products where I am a:'
                        : 'Show only datasets where I am a:',
                )}
            </Typography.Text>
            <Select
                placeholder={t('Select roles')}
                value={selectedRole || undefined}
                onChange={handleRoleFilterChange}
                options={uniqueUserRoles.map((role) => ({ label: role.label, value: role.value }))}
                style={{ minWidth: 200 }}
                allowClear
            />
        </Space>
    );
}
