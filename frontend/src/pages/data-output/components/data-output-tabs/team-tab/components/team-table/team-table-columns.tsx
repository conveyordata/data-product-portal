// import {
//     DataOutputMembershipRole,
//     DataOutputMembershipStatus,
//     DataOutputUserMembership,
// } from '@/types/data-output-membership';
import { TFunction } from 'i18next';
import { Badge, Button, Popconfirm, Space, TableColumnsType } from 'antd';
import { UserAvatar } from '@/components/user-avatar/user-avatar.component.tsx';
import { RoleChangeForm } from '@/pages/data-output/components/data-output-tabs/team-tab/components/role-change-form/role-change-form.tsx';
// import { getDataOutputMembershipBadgeStatus, getDataOutputMembershipStatusLabel } from '@/utils/status.helper.ts';

type Props = {
    t: TFunction;
    onRemoveMembership: (userId: string) => void;
    onAcceptMembershipRequest: (userId: string) => void;
    onRejectMembershipRequest: (userId: string) => void;
    onRoleChange: (role: DataOutputMembershipRole, membershipId: string) => void;
    isRemovingUser: boolean;
    dataOutputUsers: DataOutputUserMembership[];
    canPerformTeamActions: (userId: string) => boolean;
    isLoading?: boolean;
    hasCurrentUserMembership: boolean;
};

export const getDataOutputUsersTableColumns = ({
    t,
    onRemoveMembership,
    onAcceptMembershipRequest,
    onRejectMembershipRequest,
    isLoading = false,
    onRoleChange,
    isRemovingUser,
    dataOutputUsers,
    canPerformTeamActions,
    hasCurrentUserMembership,
}: Props): TableColumnsType<DataOutputUserMembership> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'user.first_name',
            render: (_, { user, status }) => {
                const isNotApproved = status !== DataOutputMembershipStatus.Approved;
                return (
                    <UserAvatar
                        name={`${user.first_name} ${user.last_name}`}
                        email={user.email}
                        linkProps={isNotApproved ? { type: 'secondary' } : undefined}
                        textProps={isNotApproved ? { type: 'secondary' } : undefined}
                    />
                );
            },
            sorter: (a, b) => a.user.last_name.localeCompare(b.user.last_name),
            width: '50%',
        },
        {
            title: t('Role'),
            dataIndex: 'role',
            render: (role: DataOutputMembershipRole, { user, id, status }) => {
                const isApproved = status === DataOutputMembershipStatus.Approved;
                return (
                    <RoleChangeForm
                        initialRole={role}
                        userId={user.id}
                        dataOutputUsers={dataOutputUsers}
                        onRoleChange={(role) => onRoleChange(role, id)}
                        isDisabled={!canPerformTeamActions(user.id) || !isApproved}
                    />
                );
            },
            width: '25%',
        },
        {
            title: t('Status'),
            dataIndex: 'status',
            render: (status: DataOutputMembershipStatus) => {
                return (
                    <Badge
                        status={getDataOutputMembershipBadgeStatus(status)}
                        text={getDataOutputMembershipStatusLabel(status)}
                    />
                );
            },
            width: '20%',
        },
        {
            title: t('Actions'),
            key: 'action',
            hidden: !hasCurrentUserMembership,
            render: (_, { user, status, id }) => (
                <Space>
                    {status === DataOutputMembershipStatus.Pending ? (
                        <Space>
                            <Popconfirm
                                title={t('Remove User')}
                                description={t('Are you sure you want to allow access to user {{name}}?', {
                                    name: user.first_name,
                                })}
                                onConfirm={() => onAcceptMembershipRequest(id)}
                                placement={'leftTop'}
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                                okButtonProps={{ loading: isLoading }}
                                autoAdjustOverflow={true}
                            >
                                <Button
                                    loading={isLoading}
                                    disabled={isLoading || !canPerformTeamActions(user.id)}
                                    type={'link'}
                                >
                                    {t('Accept')}
                                </Button>
                            </Popconfirm>
                            <Popconfirm
                                title={t('Remove User')}
                                description={t('Are you sure you want to deny access to user {{name}}?', {
                                    name: user.first_name,
                                })}
                                onConfirm={() => onRejectMembershipRequest(id)}
                                placement={'leftTop'}
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                                okButtonProps={{ loading: isLoading }}
                                autoAdjustOverflow={true}
                            >
                                <Button
                                    loading={isLoading}
                                    disabled={isLoading || !canPerformTeamActions(user.id)}
                                    type={'link'}
                                >
                                    {t('Reject')}
                                </Button>
                            </Popconfirm>
                        </Space>
                    ) : (
                        <Popconfirm
                            title={t('Remove User')}
                            description={t('Are you sure you want to remove {{name}} from the data output?', {
                                name: user.first_name,
                            })}
                            onConfirm={() => onRemoveMembership(id)}
                            placement={'leftTop'}
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            okButtonProps={{ loading: isRemovingUser }}
                            autoAdjustOverflow={true}
                        >
                            <Button
                                loading={isRemovingUser}
                                disabled={isRemovingUser || !canPerformTeamActions(user.id)}
                                type={'link'}
                            >
                                {t('Remove')}
                            </Button>
                        </Popconfirm>
                    )}
                </Space>
            ),
        },
    ];
};
