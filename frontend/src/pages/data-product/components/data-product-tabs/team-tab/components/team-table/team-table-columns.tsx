import { Badge, Button, Popconfirm, Space, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { RoleChangeForm } from '@/components/roles/role-change-form/role-change-form';
import { UserAvatar } from '@/components/user-avatar/user-avatar.component.tsx';
import { DecisionStatus, type RoleContract } from '@/types/roles';
import { type DataProductRoleAssignmentContract, Prototype } from '@/types/roles/role.contract';
import { getRoleAssignmentBadgeStatus, getRoleAssignmentStatusLabel } from '@/utils/status.helper';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    dataProductUsers: DataProductRoleAssignmentContract[];
    onRemoveUserAccess: (assignmentId: string) => void;
    onAcceptAccessRequest: (assignmentId: string) => void;
    onRejectAccessRequest: (assignmentId: string) => void;
    onRoleChange: (role: RoleContract, assignmentId: string) => void;
    isRemovingUser: boolean;
    isLoading: boolean;
    canApprove: boolean;
    canEdit: boolean;
    canRemove: boolean;
};
export const getDataProductUsersTableColumns = ({
    t,
    dataProductUsers,
    onRemoveUserAccess,
    onAcceptAccessRequest,
    onRejectAccessRequest,
    isLoading,
    onRoleChange,
    isRemovingUser,
    canEdit,
    canRemove,
    canApprove,
}: Props): TableColumnsType<DataProductRoleAssignmentContract> => {
    const sorter = new Sorter<DataProductRoleAssignmentContract>();
    const numberOfOwners = dataProductUsers.filter(
        (assignment) => assignment.role.prototype === Prototype.OWNER,
    ).length;
    const lockOwners = numberOfOwners <= 1;

    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'user.first_name',
            render: (_, { user, decision: status }) => {
                const isNotApproved = status !== DecisionStatus.Approved;
                return (
                    <UserAvatar
                        name={`${user.first_name} ${user.last_name}`}
                        email={user.email}
                        linkProps={isNotApproved ? { type: 'secondary' } : undefined}
                        textProps={isNotApproved ? { type: 'secondary' } : undefined}
                    />
                );
            },
            width: '50%',
            sorter: sorter.cascadedSorter(
                sorter.stringSorter((assignment) => assignment.user.last_name),
                sorter.stringSorter((assignment) => assignment.user.first_name),
            ),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Role'),
            dataIndex: 'role',
            render: (role: RoleContract, { id, decision }: DataProductRoleAssignmentContract) => {
                const isApproved = decision === DecisionStatus.Approved;
                const disabled = role.prototype === Prototype.OWNER && lockOwners;

                return (
                    <RoleChangeForm
                        initialRole={role}
                        onRoleChange={(role) => onRoleChange(role, id)}
                        disabled={disabled || !canEdit || !isApproved}
                        scope={'data_product'}
                    />
                );
            },
            width: '25%',
            ...new FilterSettings(dataProductUsers, (assignment) => assignment.role.name),
            sorter: sorter.stringSorter((assignment) => assignment.role.name),
        },
        {
            title: t('Status'),
            dataIndex: 'decision',
            render: (decision: DecisionStatus) => {
                return (
                    <Badge
                        status={getRoleAssignmentBadgeStatus(decision)}
                        text={getRoleAssignmentStatusLabel(t, decision)}
                    />
                );
            },
            width: '20%',
            ...new FilterSettings(dataProductUsers, (assignment) =>
                getRoleAssignmentStatusLabel(t, assignment.decision),
            ),
            sorter: sorter.stringSorter((assignment) => getRoleAssignmentStatusLabel(t, assignment.decision)),
        },
        {
            title: t('Actions'),
            key: 'action',
            hidden: !(canRemove || canApprove),
            render: (_, { user, id, decision }: DataProductRoleAssignmentContract) => (
                <Space>
                    {decision === DecisionStatus.Pending ? (
                        <Space>
                            <Popconfirm
                                title={t('Allow User')}
                                description={t('Are you sure you want to allow access to user {{name}}?', {
                                    name: user.first_name,
                                })}
                                onConfirm={() => onAcceptAccessRequest(id)}
                                placement={'leftTop'}
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                                okButtonProps={{ loading: isLoading }}
                                autoAdjustOverflow={true}
                            >
                                <Button loading={isLoading} disabled={isLoading || !canApprove} type={'link'}>
                                    {t('Accept')}
                                </Button>
                            </Popconfirm>
                            <Popconfirm
                                title={t('Remove User')}
                                description={t('Are you sure you want to deny access to user {{name}}?', {
                                    name: user.first_name,
                                })}
                                onConfirm={() => onRejectAccessRequest(id)}
                                placement={'leftTop'}
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                                okButtonProps={{ loading: isLoading }}
                                autoAdjustOverflow={true}
                            >
                                <Button loading={isLoading} disabled={isLoading || !canApprove} type={'link'}>
                                    {t('Reject')}
                                </Button>
                            </Popconfirm>
                        </Space>
                    ) : (
                        <Popconfirm
                            title={t('Remove User')}
                            description={t('Are you sure you want to remove {{name}} from the data product?', {
                                name: user.first_name,
                            })}
                            onConfirm={() => onRemoveUserAccess(id)}
                            placement={'leftTop'}
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            okButtonProps={{ loading: isRemovingUser }}
                            autoAdjustOverflow={true}
                        >
                            <Button loading={isRemovingUser} disabled={isRemovingUser || !canRemove} type={'link'}>
                                {t('Remove')}
                            </Button>
                        </Popconfirm>
                    )}
                </Space>
            ),
        },
    ];
};
