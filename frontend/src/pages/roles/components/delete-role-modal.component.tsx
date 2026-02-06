import { Alert, Badge, Button, List, Skeleton, Space, Typography, theme } from 'antd';
import { useMemo } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { FormModal } from '@/components/modal/form-modal/form-modal.component';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import {
    type DataProduct,
    type OutputPort,
    useListDataProductRoleAssignmentsQuery,
    useListGlobalRoleAssignmentsQuery,
    useListOutputPortRoleAssignmentsQuery,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi';
import { type Role, useRemoveRoleMutation } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { ApplicationPaths, createDataProductIdPath, createMarketplaceOutputPortPath } from '@/types/navigation';
import { Scope } from '@/types/roles';
import styles from './delete-role-modal.module.scss';

const { Text } = Typography;

function uniqueOrderedWithCount<T extends DataProduct | OutputPort>(array: T[] | undefined): (T & { count: number })[] {
    if (array === undefined) {
        return [];
    }

    const seen = new Map<string, number>();
    return array
        .filter((item) => {
            const fieldValue = item.id;
            if (seen.has(fieldValue)) {
                seen.set(fieldValue, (seen.get(fieldValue) ?? 0) + 1);
                return false;
            }
            seen.set(fieldValue, 1);
            return true;
        })
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((item) => ({ ...item, count: seen.get(item.id) ?? 0 }));
}

type Props = {
    role: Role;
    isOpen: boolean;
    onClose: () => void;
};
export function DeleteRoleModal({ role, isOpen, onClose }: Props) {
    const { t } = useTranslation();
    const {
        token: { colorIcon: badgeColor },
    } = theme.useToken();

    const [deleteRole, { isLoading: deleteInProgress }] = useRemoveRoleMutation();
    const { data: dataProductAssignments, isLoading: dataProductLoading } = useListDataProductRoleAssignmentsQuery(
        { roleId: role.id },
        { skip: role.scope !== Scope.DATA_PRODUCT },
    );
    const { data: datasetAssignments, isLoading: datasetLoading } = useListOutputPortRoleAssignmentsQuery(
        { roleId: role.id },
        { skip: role.scope !== Scope.DATASET },
    );
    const { data: globalAssignments, isLoading: globalLoading } = useListGlobalRoleAssignmentsQuery(
        { roleId: role.id },
        { skip: role.scope !== Scope.GLOBAL },
    );

    const assignments = (() => {
        switch (role.scope) {
            case Scope.GLOBAL:
                return globalAssignments?.role_assignments;
            case Scope.DATA_PRODUCT:
                return dataProductAssignments?.role_assignments;
            case Scope.DATASET:
                return datasetAssignments?.role_assignments;
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
                return t('Delete {{ name }} Data Product role', { name: role.name });
            case Scope.DATASET:
                return t('Delete {{ name }} Output Port role', { name: role.name });
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
                        <Text>{t('Please have a look at the following Data Products:')}</Text>
                        <List
                            bordered
                            dataSource={uniqueOrderedWithCount(
                                dataProductAssignments?.role_assignments?.map((assignment) => assignment.data_product),
                            )}
                            renderItem={(item: DataProduct & { count: number }) => (
                                <List.Item>
                                    <Link to={createDataProductIdPath(item.id, DataProductTabKeys.Team)}>
                                        {item.name}
                                    </Link>
                                    <Badge count={item.count} color={badgeColor} />
                                </List.Item>
                            )}
                        />
                    </>
                );
            case Scope.DATASET:
                return (
                    <>
                        <Text>{t('Please have a look at the following Output Ports:')}</Text>
                        <List
                            bordered
                            dataSource={uniqueOrderedWithCount(
                                datasetAssignments?.role_assignments?.map((assignment) => assignment.output_port),
                            )}
                            renderItem={(item: OutputPort & { count: number }) => (
                                <List.Item>
                                    <Link
                                        to={createMarketplaceOutputPortPath(
                                            item.id,
                                            item.data_product_id,
                                            DatasetTabKeys.Team,
                                        )}
                                    >
                                        {item.name}
                                    </Link>
                                    <Badge count={item.count} color={badgeColor} />
                                </List.Item>
                            )}
                        />
                    </>
                );
        }
    }, [role, dataProductAssignments, datasetAssignments, t, badgeColor]);

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
                <Space orientation="vertical" size="middle">
                    <Alert
                        showIcon
                        type="success"
                        title={t('No assignments found for the {{ name }} role.', {
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
                <Space orientation="vertical" size="middle">
                    <Alert
                        showIcon
                        type="warning"
                        title={t('This role still has {{ count }} assignments.', {
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
