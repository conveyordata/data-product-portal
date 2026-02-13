import { usePostHog } from '@posthog/react';
import { Select } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { PosthogEvents } from '@/constants/posthog.constants';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import {
    type DataProductRoleAssignmentResponse,
    type OutputPortRoleAssignmentResponse,
    useListDataProductRoleAssignmentsQuery,
    useListOutputPortRoleAssignmentsQuery,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';

interface RoleFilterProps {
    selectedRoles: string[];
    onRoleChange: (selected: { productIds: string[]; roles: string[] }) => void;
    mode: 'data_products' | 'datasets';
}

export function RoleFilter({ selectedRoles, onRoleChange, mode }: RoleFilterProps) {
    const { t } = useTranslation();
    const posthog = usePostHog();

    const currentUser = useSelector(selectCurrentUser);
    const { data: userDatasetRoles = undefined } = useListOutputPortRoleAssignmentsQuery(
        { userId: currentUser?.id || '' },
        { skip: !currentUser || mode !== 'datasets' },
    );
    const { data: userDataProductRoles = undefined } = useListDataProductRoleAssignmentsQuery(
        { userId: currentUser?.id || '' },
        { skip: !currentUser || mode !== 'data_products' },
    );

    const uniqueUserRoles = useMemo(() => {
        const userRoles =
            mode === 'data_products' ? userDataProductRoles?.role_assignments : userDatasetRoles?.role_assignments;
        if (!userRoles?.length) return [];

        const uniqueRoles = new Map<string, { label: string; value: string; productIds: string[] }>();

        const get_id = (assignment: DataProductRoleAssignmentResponse | OutputPortRoleAssignmentResponse): string => {
            if (mode === 'data_products') {
                return (assignment as DataProductRoleAssignmentResponse).data_product.id;
            }
            if (mode === 'datasets') {
                return (assignment as OutputPortRoleAssignmentResponse).output_port.id;
            }
            throw new Error('Invalid assignment type for mode');
        };

        userRoles.forEach((assignment) => {
            const roleId = assignment.role?.id || '';
            const productId = get_id(assignment);
            const roleName = assignment.role?.name || '';
            if (!uniqueRoles.has(roleId)) {
                uniqueRoles.set(roleId, { label: roleName, value: roleId, productIds: [productId] });
            } else {
                uniqueRoles.get(roleId)?.productIds.push(productId);
            }
        });

        return Array.from(uniqueRoles.values()).sort((a, b) => a.label.localeCompare(b.label));
    }, [userDataProductRoles, userDatasetRoles, mode]);

    if (uniqueUserRoles.length === 0) {
        return null;
    }

    const handleRoleFilterChange = (roleIds: string[]) => {
        const event =
            mode === 'data_products' ? PosthogEvents.DATA_PRODUCTS_FILTER_USED : PosthogEvents.MARKETPLACE_FILTER_USED;
        posthog.capture(event, {
            filter_type: 'roles',
            filter_value: roleIds,
        });

        // Get all product IDs for the selected roles
        const allProductIds = roleIds.flatMap((roleId) => {
            const roleData = uniqueUserRoles.find((role) => role.value === roleId);
            return roleData ? roleData.productIds : [];
        });

        onRoleChange({ productIds: allProductIds, roles: roleIds });
    };

    const options = uniqueUserRoles.map((role) => ({
        label: role.label,
        value: role.value,
    }));

    return (
        <Select
            mode="multiple"
            placeholder={t('Filter by role')}
            value={selectedRoles}
            onChange={handleRoleFilterChange}
            options={options}
            style={{ minWidth: 200 }}
            allowClear
        />
    );
}
