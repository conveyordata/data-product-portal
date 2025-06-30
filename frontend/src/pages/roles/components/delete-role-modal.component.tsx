import { Button, Skeleton, Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { FormModal } from '@/components/modal/form-modal/form-modal.component.tsx';
import styles from '@/pages/roles/components/create-role-modal.module.scss';
import { useGetDataProductRoleAssignmentsQuery } from '@/store/features/role-assignments/data-product-roles-api-slice.ts';
import { useGetDatasetRoleAssignmentsQuery } from '@/store/features/role-assignments/dataset-roles-api-slice.ts';
import { useGetGlobalRoleAssignmentsQuery } from '@/store/features/role-assignments/global-roles-api-slice.ts';
import { useDeleteRoleMutation } from '@/store/features/roles/roles-api-slice.ts';
import { type RoleContract, Scope } from '@/types/roles';

const { Text } = Typography;

type Props = {
    role: RoleContract;
    isOpen: boolean;
    onClose: () => void;
};
export function DeleteRoleModal({ role, isOpen, onClose }: Props) {
    const { t } = useTranslation();

    const [deleteRole, { isLoading: deleteInProgress }] = useDeleteRoleMutation();
    const { data: dataProductAssignments, isLoading: dataProductLoading } = useGetDataProductRoleAssignmentsQuery(
        { role_id: role.id },
        { skip: role.scope !== Scope.DATA_PRODUCT },
    );
    const { data: datasetAssignments, isLoading: datasetLoading } = useGetDatasetRoleAssignmentsQuery(
        { role_id: role.id },
        { skip: role.scope !== Scope.DATASET },
    );
    const { data: globalAssignments, isLoading: globalLoading } = useGetGlobalRoleAssignmentsQuery(
        { role_id: role.id },
        { skip: role.scope !== Scope.GLOBAL },
    );

    const assignments = (() => {
        switch (role.scope) {
            case Scope.GLOBAL:
                return globalAssignments;
            case Scope.DATA_PRODUCT:
                return dataProductAssignments;
            case Scope.DATASET:
                return datasetAssignments;
        }
    })();

    const isLoading = (() => {
        switch (role.scope) {
            case Scope.GLOBAL:
                return globalLoading;
            case Scope.DATA_PRODUCT:
                return dataProductLoading;
            case Scope.DATASET:
                return datasetLoading;
        }
    })();

    const title = useMemo(() => {
        switch (role.scope) {
            case 'global':
                return t('Delete {{ name }} global role', { name: role.name });
            case 'data_product':
                return t('Delete {{ name }} data product role', { name: role.name });
            case 'dataset':
                return t('Delete {{ name }} dataset role', { name: role.name });
        }
    }, [role, t]);

    const handleCancel = (): void => {
        onClose();
    };

    const handleSubmit = (): void => {
        deleteRole(role.id).then(onClose);
    };

    const footer = [
        <Button className={styles.formButton} key="cancel" onClick={handleCancel}>
            {t('Cancel')}
        </Button>,
        <Button
            className={styles.formButton}
            key="submit"
            onClick={handleSubmit}
            type="primary"
            loading={deleteInProgress}
            disabled={isLoading}
            danger
        >
            {t('Delete')}
        </Button>,
    ];

    return (
        <FormModal title={title} isOpen={isOpen} onClose={onClose} footer={footer}>
            {isLoading ? (
                <Skeleton active />
            ) : assignments?.length === 0 ? (
                <Text>
                    {t('No assignment found for the {{ name }} role. No users will be impacted.', { name: role.name })}
                </Text>
            ) : (
                <Text>
                    {t(
                        'Still found {{ amount }} assignments for the {{ name }} role. Deleting this role will cause these users to lose their assignment.',
                        { amount: assignments?.length, name: role.name },
                    )}
                </Text>
            )}
        </FormModal>
    );
}
