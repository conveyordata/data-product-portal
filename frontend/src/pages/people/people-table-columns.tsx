import { Checkbox, Flex, Select, type TableColumnsType, Tooltip } from 'antd';
import type { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import type { GlobalRoleAssignmentResponse } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import type { Role } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { DecisionStatus, type GlobalRoleAssignment, Prototype } from '@/types/roles';
import { getIdentityDisplayName, getIdentityTypeLabel, type Identity } from '@/utils/identity.ts';
import { FilterSettings } from '@/utils/table-filter.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';
import styles from './people-table.module.scss';

type SelectorProps = {
    role: GlobalRoleAssignment | null;
    options: { label: string; value: string }[];
    onChange: (value: string) => void;
    disabled?: boolean;
    disabledReason?: string;
};
function RoleSelector({ role, options, onChange, disabled = false, disabledReason }: SelectorProps) {
    return (
        <Tooltip title={disabledReason}>
            <Select
                className={styles.select}
                value={
                    role && role.decision !== DecisionStatus.Approved
                        ? null
                        : role?.role.prototype === Prototype.ADMIN
                          ? ''
                          : (role?.role.id ?? '')
                }
                placeholder={role?.role.name}
                options={options}
                onChange={(value: string) => onChange(value)}
                disabled={disabled || !!disabledReason}
            />
        </Tooltip>
    );
}

export const getPeopleTableColumns = ({
    t,
    identities: data,
    assignments,
    canAssignRole,
    canDeleteRole,
    allRoles,
    onChange,
    changeCheckbox,
    isSaving,
}: {
    t: TFunction;
    identities: Identity[];
    assignments: GlobalRoleAssignmentResponse[];
    canAssignRole: boolean;
    canDeleteRole: boolean;
    allRoles: Role[];
    onChange: (identity_id: string, value: string, original: GlobalRoleAssignment | null) => void;
    changeCheckbox: (user_id: string, can_become_admin: boolean) => void;
    isSaving: boolean;
}): TableColumnsType<Identity> => {
    const sorter = new Sorter<Identity>();
    const emailOrExternalId = (identity: Identity) =>
        identity.type === 'user' ? identity.email : identity.external_id;
    const assignmentsByIdentity = new Map(assignments.map((assignment) => [assignment.identity.id, assignment]));
    const roleFor = (identity: Identity) => assignmentsByIdentity.get(identity.id) ?? null;
    const everyone = allRoles.find((role) => role.prototype === Prototype.EVERYONE);
    const options = allRoles.map((role) => ({
        label: role.name,
        value: role.prototype === Prototype.EVERYONE ? '' : role.id,
    }));

    const columns: TableColumnsType<Identity> = [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            ellipsis: { showTitle: false },
            render: (_, record) => {
                return <TableCellItem text={getIdentityDisplayName(record)} />;
            },
            sorter: { compare: sorter.stringSorter(getIdentityDisplayName), multiple: 1 },
            defaultSortOrder: 'ascend',
            sortDirections: ['ascend', 'descend', 'ascend'],
        },
        {
            title: t('Identifier'),
            key: 'email_or_external_id',
            ellipsis: { showTitle: false },
            render: (_, identity) => {
                const text = emailOrExternalId(identity);
                return <TableCellItem text={text} tooltip={{ content: text }} />;
            },
            sorter: {
                compare: sorter.stringSorter(emailOrExternalId),
                multiple: 3,
            },
        },
        {
            title: t('Type'),
            key: 'type',
            width: '15%',
            render: (_, identity) => <TableCellItem text={getIdentityTypeLabel(identity, t)} />,
            ...new FilterSettings(data, (identity) => getIdentityTypeLabel(identity, t)),
            sorter: { compare: sorter.stringSorter((identity) => getIdentityTypeLabel(identity, t)), multiple: 4 },
        },
        {
            title: t('Global Role'),
            dataIndex: 'global_role',
            ellipsis: { showTitle: false },
            width: '15%',
            sorter: {
                compare: sorter.stringSorter((identity) => roleFor(identity)?.role.name ?? everyone?.name),
                multiple: 2,
            },
            render: (_, identity) => {
                const role = roleFor(identity);
                let name = role?.role.name;
                if (role?.role.prototype === Prototype.ADMIN) {
                    name = everyone?.name;
                }
                if (canAssignRole) {
                    return (
                        <TableCellItem>
                            <RoleSelector
                                role={role}
                                onChange={(value: string) => onChange(identity.id, value, role)}
                                options={options}
                                disabled={isSaving}
                                disabledReason={
                                    role?.decision === DecisionStatus.Denied && !canDeleteRole
                                        ? t(
                                              'This role was previously rejected. You don’t have enough permission to modify it.',
                                          )
                                        : undefined
                                }
                            />
                        </TableCellItem>
                    );
                }
                return <TableCellItem text={name || everyone?.name} />;
            },
        },
    ];

    if (canAssignRole) {
        columns.push({
            title: t('Can become admin'),
            dataIndex: 'can_become_admin',
            ellipsis: { showTitle: false },
            width: 160,
            render: (_, user) => {
                if (user.type !== 'user') return null;
                return (
                    <Flex justify="center">
                        <Checkbox
                            checked={user.can_become_admin}
                            disabled={isSaving}
                            onChange={(e) => changeCheckbox(user.id, e.target.checked)}
                        />
                    </Flex>
                );
            },
        });
    }

    return columns;
};
