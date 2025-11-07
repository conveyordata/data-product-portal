import { DownOutlined } from '@ant-design/icons';
import { Button, Dropdown, type MenuProps, Radio } from 'antd';
import type { RadioChangeEvent } from 'antd/lib';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useGetDataProductRoleAssignmentsQuery } from '@/store/features/role-assignments/data-product-roles-api-slice';
import { useGetDatasetRoleAssignmentsQuery } from '@/store/features/role-assignments/dataset-roles-api-slice';
import type { DataProductRoleAssignmentContract, DatasetRoleAssignmentContract } from '@/types/roles/role.contract';
import styles from './role-filter.component.module.scss';

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

    const [dropdownOpen, setDropdownOpen] = useState(false);

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

    if (uniqueUserRoles.length === 0) {
        return <div style={{ display: 'flex' }} />;
    }

    const menuItems: MenuProps['items'] = uniqueUserRoles.map((role) => ({
        key: role.value,
        label: <span className={selectedRole === role.value ? styles.dropdownSelected : undefined}>{role.label}</span>,
        className: selectedRole === role.value ? styles.dropdownSelectedBg : undefined,
    }));

    const handleMenuClick: MenuProps['onClick'] = (info) => {
        handleRoleFilterChange(info.key);
    };

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

    const handleRadioChange = (e: RadioChangeEvent) => {
        if (e.target.value === 'all') {
            onRoleChange({ productIds: [], role: '' });
            setDropdownOpen(false);
        }
    };

    const handleRoleRadioClick = () => {
        setDropdownOpen(true);
    };

    const selectedRoleLabel = selectedRole
        ? uniqueUserRoles.find((role) => role.value === selectedRole)?.label
        : undefined;

    const isRoleSelected = !!selectedRole;

    return (
        <Radio.Group
            value={selectedRole ? 'role' : 'all'}
            onChange={handleRadioChange}
            optionType="button"
            buttonStyle="solid"
            size={'middle'}
        >
            <Radio.Button value="all">{t('Show all')}</Radio.Button>
            <Radio.Button value="role" className={styles.radioDropdownButton} onClick={handleRoleRadioClick}>
                <Dropdown
                    menu={{
                        items: menuItems,
                        onClick: (info) => {
                            handleMenuClick(info);
                            setDropdownOpen(false);
                        },
                        selectable: true,
                        selectedKeys: selectedRole ? [selectedRole] : [],
                    }}
                    open={dropdownOpen}
                    onOpenChange={setDropdownOpen}
                    trigger={['click']}
                >
                    <Button
                        type="text"
                        className={`${styles.dropdownButton} ${isRoleSelected ? styles.dropdownButtonSelected : ''}`}
                        onClick={(e) => e.stopPropagation()}
                    >
                        {t('Only where I am ')}
                        {selectedRoleLabel && (
                            <>
                                {' > '}
                                <span>{selectedRoleLabel}</span>
                            </>
                        )}
                        <DownOutlined />
                    </Button>
                </Dropdown>
            </Radio.Button>
        </Radio.Group>
    );
}
