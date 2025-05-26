import { Badge, Button, Popconfirm, Space, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { RoleChangeForm } from '@/components/roles/role-change-form/role-change-form.tsx';
import { UserAvatar } from '@/components/user-avatar/user-avatar.component.tsx';
import { DecisionStatus } from '@/types/roles';
import type { DatasetRoleAssignmentContract, RoleContract } from '@/types/roles/role.contract.ts';
import { getRoleAssignmentBadgeStatus, getRoleAssignmentStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    datasetUsers: DatasetRoleAssignmentContract[];
    onRemoveUserAccess: (userId: string) => void;
    onAcceptAccessRequest: (assignmentId: string) => void;
    onRejectAccessRequest: (assignmentId: string) => void;
    onRoleChange: (role: RoleContract, assignmentId: string) => void;
    isRemovingUser: boolean;
    isLoading?: boolean;
    canApprove?: boolean;
    canEdit?: boolean;
    canRemove?: boolean;
};

export const getDatasetTeamColumns = ({
    t,
    datasetUsers,
    onRemoveUserAccess,
    onAcceptAccessRequest,
    onRejectAccessRequest,
    onRoleChange,
    isRemovingUser,
    isLoading,
    canApprove,
    canEdit,
    canRemove,
}: Props): TableColumnsType<DatasetRoleAssignmentContract> => {
    const sorter = new Sorter<DatasetRoleAssignmentContract>();
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
            sorter: sorter.stringSorter((assignment) => assignment.user.last_name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Role'),
            dataIndex: 'role',
            render: (role: RoleContract, { user, id, decision }: DatasetRoleAssignmentContract) => {
                const isApproved = decision === DecisionStatus.Approved;
                return (
                    <RoleChangeForm<DatasetRoleAssignmentContract>
                        initialRole={role}
                        userId={user.id}
                        onRoleChange={(role) => onRoleChange(role, id)}
                        isDisabled={!canEdit || !isApproved}
                        scope={'dataset'}
                    />
                );
            },
            width: '25%',
            ...new FilterSettings(datasetUsers, (assignment) => assignment.role.name),
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
            ...new FilterSettings(datasetUsers, (assignment) => getRoleAssignmentStatusLabel(t, assignment.decision)),
            sorter: sorter.stringSorter((membership) => getRoleAssignmentStatusLabel(t, membership.decision)),
        },
        {
            title: t('Actions'),
            key: 'action',
            hidden: !(canRemove || canApprove),
            render: (_, { user, id, decision }: DatasetRoleAssignmentContract) => (
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
                            description={t('Are you sure you want to remove {{name}} from the dataset?', {
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
