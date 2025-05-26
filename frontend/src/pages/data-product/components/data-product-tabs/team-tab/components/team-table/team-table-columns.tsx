import { Badge, Button, Popconfirm, Space, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { UserAvatar } from '@/components/user-avatar/user-avatar.component.tsx';
import { RoleChangeForm } from '@/pages/data-product/components/data-product-tabs/team-tab/components/role-change-form/role-change-form';
import { DecisionStatus, type RoleContract } from '@/types/roles';
import type { DataProductRoleAssignmentContract } from '@/types/roles/role.contract';
import { getDataProductMembershipBadgeStatus, getDataProductMembershipStatusLabel } from '@/utils/status.helper';
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
    isLoading?: boolean;
    canEdit?: boolean;
    canRemove?: boolean;
    canApprove?: boolean;
};
export const getDataProductUsersTableColumns = ({
    t,
    onRemoveUserAccess,
    onAcceptAccessRequest,
    onRejectAccessRequest,
    isLoading = false,
    onRoleChange,
    isRemovingUser,
    dataProductUsers,
    canEdit,
    canRemove,
    canApprove,
}: Props): TableColumnsType<DataProductRoleAssignmentContract> => {
    const sorter = new Sorter<DataProductRoleAssignmentContract>();
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
            sorter: sorter.stringSorter((membership) => membership.user.last_name),
        },
        {
            title: t('Role'),
            dataIndex: 'role',
            render: (role: RoleContract, { user, id, decision }: DataProductRoleAssignmentContract) => {
                const isApproved = decision === DecisionStatus.Approved;
                return (
                    <RoleChangeForm
                        initialRole={role}
                        userId={user.id}
                        dataProductUsers={dataProductUsers}
                        onRoleChange={(role) => onRoleChange(role, id)}
                        isDisabled={!canEdit || !isApproved}
                    />
                );
            },
            width: '25%',
            ...new FilterSettings(dataProductUsers, (membership) => membership.role.name),
            sorter: sorter.stringSorter((membership) => membership.role.name),
        },
        {
            title: t('Status'),
            dataIndex: 'decision',
            render: (decision: DecisionStatus) => {
                return (
                    <Badge
                        status={getDataProductMembershipBadgeStatus(decision)}
                        text={getDataProductMembershipStatusLabel(t, decision)}
                    />
                );
            },
            width: '20%',
            ...new FilterSettings(dataProductUsers, (membership) =>
                getDataProductMembershipStatusLabel(t, membership.decision),
            ),
            sorter: sorter.stringSorter((membership) => getDataProductMembershipStatusLabel(t, membership.decision)),
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
