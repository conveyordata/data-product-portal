import { Button, Flex, Input } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { searchFilter } from '@/components/empty-state/empty-state.component.tsx';

import { useModal } from '@/hooks/use-modal.tsx';
import { DataProductRoleModal } from '@/pages/data-product/components/data-product-role-modal/data-product-role-modal.tsx';
import { TeamTable } from '@/pages/data-product/components/data-product-tabs/team-tab/components/team-table/team-table.component.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { useListDataProductRoleAssignmentsQuery } from '@/store/api/services/generated/authorizationRoleAssignmentsApi';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { identityMatchesSearch } from '@/utils/identity.ts';
import styles from './team-tab.module.scss';

type Props = {
    dataProductId: string;
};
export function TeamTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { isVisible, handleOpen, handleClose } = useModal();
    const roleAssignmentsQuery = useListDataProductRoleAssignmentsQuery({
        dataProductId: dataProductId,
    });
    const { data: roleAssignments } = roleAssignmentsQuery;
    const [searchTerm, setSearchTerm] = useState<string>('');
    const filteredAssignments = useMemo(
        () =>
            roleAssignments?.role_assignments.filter((assignment) =>
                identityMatchesSearch(assignment.identity, searchTerm),
            ) ?? [],
        [roleAssignments, searchTerm],
    );
    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__CREATE_USER,
        },
        { skip: !dataProductId },
    );

    const canAssign = access?.allowed === true;

    return (
        <>
            <Flex vertical gap="middle">
                <Flex gap="small">
                    <Input.Search
                        placeholder={t('Search by name or email')}
                        allowClear
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <Button type="primary" className={styles.formButton} onClick={handleOpen} disabled={!canAssign}>
                        {t('Add team member')}
                    </Button>
                </Flex>
                <TeamTable
                    dataProductId={dataProductId}
                    assignments={roleAssignments?.role_assignments ?? []}
                    filteredAssignments={filteredAssignments}
                    roleAssignmentsQuery={roleAssignmentsQuery}
                    filter={searchFilter(searchTerm, setSearchTerm)}
                />
            </Flex>
            {isVisible && <DataProductRoleModal dataProductId={dataProductId} mode="assign" onClose={handleClose} />}
        </>
    );
}
