import { Alert, Button, List, Skeleton, Space, Typography } from 'antd';
import { useMemo } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { FormModal } from '@/components/modal/form-modal/form-modal.component.tsx';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { useGetDataProductRoleAssignmentsQuery } from '@/store/features/role-assignments/data-product-roles-api-slice.ts';
import { useGetDatasetRoleAssignmentsQuery } from '@/store/features/role-assignments/dataset-roles-api-slice.ts';
import { useGetGlobalRoleAssignmentsQuery } from '@/store/features/role-assignments/global-roles-api-slice.ts';
import { useDeleteRoleMutation } from '@/store/features/roles/roles-api-slice.ts';
import type { DataProductContract } from '@/types/data-product';
import type { DatasetContract } from '@/types/dataset';
import { ApplicationPaths, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation.ts';
import { type RoleContract, Scope } from '@/types/roles';
import styles from './delete-role-modal.module.scss';

const { Text } = Typography;

function uniqueOrdered<T extends DataProductContract | DatasetContract>(array: T[] | undefined): T[] {
    if (array === undefined) {
        return [];
    }

    const seen = new Set<string>();
    return array
        .filter((item) => {
            const fieldValue = item.id;
            if (seen.has(fieldValue)) {
                return false;
            }
            seen.add(fieldValue);
            return true;
        })
        .sort((a, b) => a.name.localeCompare(b.name));
}

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

    const numAssignments = assignments?.length ?? 0;

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
            case Scope.GLOBAL:
                return t('Delete {{ name }} global role', { name: role.name });
            case Scope.DATA_PRODUCT:
                return t('Delete {{ name }} data product role', { name: role.name });
            case Scope.DATASET:
                return t('Delete {{ name }} dataset role', { name: role.name });
        }
    }, [role, t]);

    const additionalInfo = useMemo(() => {
        switch (role.scope) {
            case Scope.GLOBAL:
                return (
                    <Text>
                        <Trans t={t}>
                            Please have a look at the <Link to={ApplicationPaths.People}>People</Link> page.
                        </Trans>
                    </Text>
                );
            case Scope.DATA_PRODUCT:
                return (
                    <>
                        <Text>{t('Please have a look at the following data products:')}</Text>
                        <List
                            bordered
                            dataSource={uniqueOrdered(
                                dataProductAssignments?.map((assignment) => assignment.data_product),
                            )}
                            renderItem={(item: DataProductContract) => (
                                <List.Item>
                                    <Link to={createDataProductIdPath(item.id, DataProductTabKeys.Team)}>
                                        {item.name}
                                    </Link>
                                </List.Item>
                            )}
                        />
                    </>
                );
            case Scope.DATASET:
                return (
                    <>
                        <Text>{t('Please have a look at the following datasets:')}</Text>
                        <List
                            bordered
                            dataSource={uniqueOrdered(datasetAssignments?.map((assignment) => assignment.dataset))}
                            renderItem={(item: DatasetContract) => (
                                <List.Item>
                                    <Link to={createDatasetIdPath(item.id, DatasetTabKeys.Team)}>{item.name}</Link>
                                </List.Item>
                            )}
                        />
                    </>
                );
        }
    }, [role, dataProductAssignments, datasetAssignments, t]);

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
            disabled={isLoading || numAssignments > 0}
            danger
        >
            {t('Delete Role')}
        </Button>,
    ];

    return (
        <FormModal title={title} isOpen={isOpen} onClose={onClose} footer={footer}>
            {isLoading ? (
                <Skeleton active />
            ) : assignments?.length === 0 ? (
                <Space direction="vertical" size={'middle'}>
                    <Alert
                        showIcon
                        type="success"
                        message={t('No assignments found for the {{ name }} role.', {
                            name: role.name,
                        })}
                    />
                    <Text>
                        {t(
                            'There are no users that have this role assigned. The role can be safely removed, but be aware that this cannot be undone.',
                        )}
                    </Text>
                </Space>
            ) : (
                <Space direction="vertical" size={'middle'}>
                    <Alert
                        showIcon
                        type="warning"
                        message={t('This role still has {{ count }} assignments.', {
                            count: numAssignments,
                        })}
                    />
                    <Text>
                        {t(
                            'This role is currently still assigned to {{ count }} users. Deletion of the {{ name }} role is only possible after these users have been assigned a new role.',
                            {
                                count: numAssignments,
                                name: role.name,
                            },
                        )}
                    </Text>
                    {additionalInfo}
                </Space>
            )}
        </FormModal>
    );
}
