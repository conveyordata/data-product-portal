import { Badge, Button, Popconfirm, Space, type TableColumnsType, Tooltip } from 'antd';
import type { TFunction } from 'i18next';
import { IdentityAvatarWithDetails } from '@/components/identity-avatar/identity-avatar.component.tsx';
import { RoleChangeForm } from '@/components/roles/role-change-form/role-change-form';
import type { DataProductRoleAssignmentResponse } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import type { Role } from '@/store/api/services/generated/authorizationRolesApi';
import { DecisionStatus, Prototype, Scope } from '@/types/roles';
import { compareIdentities, getIdentityDisplayName, getIdentityTypeLabel } from '@/utils/identity.ts';
import { getRoleAssignmentBadgeStatus, getRoleAssignmentStatusLabel } from '@/utils/status.helper';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    assignments: DataProductRoleAssignmentResponse[];
    onRemoveAccess: (assignmentId: string) => void;
    onAcceptAccessRequest: (assignmentId: string) => void;
    onRejectAccessRequest: (assignmentId: string) => void;
    onRoleChange: (role: Role, assignmentId: string) => void;
    isSaving: boolean;
    canApprove: boolean;
    canEdit: boolean;
    canRemove: boolean;
};
export const getDataProductTeamTableColumns = ({
    t,
    assignments,
    onRemoveAccess,
    onAcceptAccessRequest,
    onRejectAccessRequest,
    isSaving,
    onRoleChange,
    canEdit,
    canRemove,
    canApprove,
}: Props): TableColumnsType<DataProductRoleAssignmentResponse> => {
    const sorter = new Sorter<DataProductRoleAssignmentResponse>();
    const numberOfOwners = assignments.filter(
        (assignment) =>
            assignment.decision === DecisionStatus.Approved && assignment.role?.prototype === Prototype.OWNER,
    ).length;
    const isLastOwner = (assignment: DataProductRoleAssignmentResponse) =>
        numberOfOwners <= 1 &&
        assignment.decision === DecisionStatus.Approved &&
        assignment.role?.prototype === Prototype.OWNER;
    const ownerRequirement = t('A Data Product must have at least one approved owner');

    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            key: 'identity',
            render: (_, { identity }) => {
                return <IdentityAvatarWithDetails identity={identity} />;
            },
            width: '50%',
            sorter: { compare: (left, right) => compareIdentities(left.identity, right.identity), multiple: 1 },
            defaultSortOrder: 'ascend',
            sortDirections: ['ascend', 'descend', 'ascend'],
        },
        {
            title: t('Type'),
            key: 'identityType',
            width: '15%',
            render: (_, { identity }) => getIdentityTypeLabel(identity, t),
            ...new FilterSettings(assignments, (assignment) => getIdentityTypeLabel(assignment.identity, t)),
            sorter: {
                compare: sorter.stringSorter((assignment) => getIdentityTypeLabel(assignment.identity, t)),
                multiple: 4,
            },
        },
        {
            title: t('Role'),
            dataIndex: 'role',
            render: (_, assignment) => {
                const { role, id, decision } = assignment;
                const locked = isLastOwner(assignment);

                return (
                    <Tooltip title={locked ? ownerRequirement : undefined}>
                        <div>
                            <RoleChangeForm
                                role={role}
                                allowOwner={assignment.identity.type === 'user'}
                                ariaLabel={t('Role for {{name}}', {
                                    name: getIdentityDisplayName(assignment.identity),
                                })}
                                onRoleChange={(role) => onRoleChange(role, id)}
                                disabled={locked || isSaving || !canEdit || decision !== DecisionStatus.Approved}
                                scope={Scope.DATA_PRODUCT}
                            />
                        </div>
                    </Tooltip>
                );
            },
            width: '20%',
            ...new FilterSettings(assignments, (assignment) => assignment.role?.name ?? t('No role assigned')),
            sorter: { compare: sorter.stringSorter((assignment) => assignment.role?.name), multiple: 3 },
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
            width: '10%',
            ...new FilterSettings(assignments, (assignment) => getRoleAssignmentStatusLabel(t, assignment.decision)),
            sorter: {
                compare: sorter.stringSorter((assignment) => getRoleAssignmentStatusLabel(t, assignment.decision)),
                multiple: 2,
            },
        },
        {
            title: t('Actions'),
            key: 'action',
            hidden: !(canRemove || canApprove),
            render: (_, assignment) => {
                const { identity, id, decision, role } = assignment;
                const locked = isLastOwner(assignment);
                return (
                    <Space>
                        {decision === DecisionStatus.Pending ? (
                            <Space>
                                <Popconfirm
                                    title={t('Approve role request')}
                                    description={t('Are you sure you want to allow access to {{name}}?', {
                                        name: getIdentityDisplayName(identity),
                                    })}
                                    onConfirm={() => onAcceptAccessRequest(id)}
                                    placement="leftTop"
                                    okText={t('Confirm')}
                                    cancelText={t('Cancel')}
                                    okButtonProps={{ loading: isSaving }}
                                    autoAdjustOverflow={true}
                                >
                                    <Button disabled={isSaving || !canApprove || !role} type="link">
                                        {t('Accept')}
                                    </Button>
                                </Popconfirm>
                                <Popconfirm
                                    title={t('Reject role request')}
                                    description={t('Are you sure you want to deny access to {{name}}?', {
                                        name: getIdentityDisplayName(identity),
                                    })}
                                    onConfirm={() => onRejectAccessRequest(id)}
                                    placement="leftTop"
                                    okText={t('Confirm')}
                                    cancelText={t('Cancel')}
                                    okButtonProps={{ loading: isSaving }}
                                    autoAdjustOverflow={true}
                                >
                                    <Button disabled={isSaving || !canApprove} type="link">
                                        {t('Reject')}
                                    </Button>
                                </Popconfirm>
                            </Space>
                        ) : (
                            <Popconfirm
                                title={t('Remove team member')}
                                description={t('Are you sure you want to remove {{name}} from the Data Product?', {
                                    name: getIdentityDisplayName(identity),
                                })}
                                onConfirm={() => onRemoveAccess(id)}
                                placement="leftTop"
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                                okButtonProps={{ loading: isSaving }}
                                autoAdjustOverflow={true}
                            >
                                <Tooltip title={locked ? ownerRequirement : undefined}>
                                    <Button disabled={locked || isSaving || !canRemove} type="link">
                                        {t('Remove')}
                                    </Button>
                                </Tooltip>
                            </Popconfirm>
                        )}
                    </Space>
                );
            },
        },
    ];
};
