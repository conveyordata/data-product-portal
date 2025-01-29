import {
    DataProductMembershipRole,
    DataProductMembershipStatus,
    DataProductUserMembership,
} from '@/types/data-product-membership';
import { TFunction } from 'i18next';
import { Badge, Button, Popconfirm, Space, TableColumnsType } from 'antd';
import { UserAvatar } from '@/components/user-avatar/user-avatar.component.tsx';
import { RoleChangeForm } from '@/pages/data-product/components/data-product-tabs/team-tab/components/role-change-form/role-change-form.tsx';
import { getDataProductMembershipBadgeStatus, getDataProductMembershipStatusLabel } from '@/utils/status.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper';
import { FilterSettings } from '@/utils/table-filter.helper';

type Props = {
    t: TFunction;
    onRemoveMembership: (userId: string) => void;
    onAcceptMembershipRequest: (userId: string) => void;
    onRejectMembershipRequest: (userId: string) => void;
    onRoleChange: (role: DataProductMembershipRole, membershipId: string) => void;
    isRemovingUser: boolean;
    dataProductUsers: DataProductUserMembership[];
    canPerformTeamActions: (userId: string) => boolean;
    isLoading?: boolean;
    hasCurrentUserMembership: boolean;
};

export const getDataProductUsersTableColumns = ({
    t,
    onRemoveMembership,
    onAcceptMembershipRequest,
    onRejectMembershipRequest,
    isLoading = false,
    onRoleChange,
    isRemovingUser,
    dataProductUsers,
    canPerformTeamActions,
    hasCurrentUserMembership,
}: Props): TableColumnsType<DataProductUserMembership> => {
    const sorter = new Sorter<DataProductUserMembership>();
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
                const isNotApproved = status !== DataProductMembershipStatus.Approved;
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
            render: (role: DataProductMembershipRole, { user, id, status }) => {
                const isApproved = status === DataProductMembershipStatus.Approved;
                return (
                    <RoleChangeForm
                        initialRole={role}
                        userId={user.id}
                        dataProductUsers={dataProductUsers}
                        onRoleChange={(role) => onRoleChange(role, id)}
                        isDisabled={!canPerformTeamActions(user.id) || !isApproved}
                    />
                );
            },
            width: '25%',
            ...new FilterSettings(dataProductUsers, (membership) => membership.role),
            sorter: sorter.stringSorter((membership) => membership.role),
        },
        {
            title: t('Status'),
            dataIndex: 'status',
            render: (status: DataProductMembershipStatus) => {
                return (
                    <Badge
                        status={getDataProductMembershipBadgeStatus(status)}
                        text={getDataProductMembershipStatusLabel(status)}
                    />
                );
            },
            width: '20%',
            ...new FilterSettings(dataProductUsers, (membership) =>
                getDataProductMembershipStatusLabel(membership.status),
            ),
            sorter: sorter.stringSorter((membership) => getDataProductMembershipStatusLabel(membership.status)),
        },
        {
            title: t('Actions'),
            key: 'action',
            hidden: !hasCurrentUserMembership,
            render: (_, { user, status, id }) => (
                <Space>
                    {status === DataProductMembershipStatus.Pending ? (
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
                            description={t('Are you sure you want to remove {{name}} from the data product?', {
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
