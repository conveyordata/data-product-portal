import { MoreOutlined } from '@ant-design/icons';
import {
    Button,
    Checkbox,
    type CheckboxChangeEvent,
    Flex,
    Popover,
    Space,
    Table,
    type TableColumnType,
    Typography,
} from 'antd';
import type { TFunction } from 'i18next';
import { type ReactElement, useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import QuestionTooltip from '@/components/tooltip/question-tooltip';
import { RoleDetailsMenu } from '@/pages/roles/components/role-details-menu.component';
import {
    type Role,
    useGetRolesQuery,
    useUpdateRoleMutation,
} from '@/store/api/services/generated/authorizationRolesApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { Prototype, Scope } from '@/types/roles';
import styles from './roles-table.module.scss';

const { Text } = Typography;

type PermissionType = 'Group' | 'Instance';

type PermissionBase = {
    type: PermissionType;
    id: AuthorizationAction | string;
    name: string;
};

type PermissionInstance = PermissionBase & {
    type: 'Instance';
    id: AuthorizationAction;
    description: string;
    access?: object;
};

type PermissionGroup = PermissionBase & {
    type: 'Group';
    id: string;
};

type Permission = PermissionInstance | PermissionGroup;

function prototypePrecedence(role_a: Role, role_b: Role) {
    const a = role_a.prototype;
    const b = role_b.prototype;

    if (a === b) {
        return 0;
    }
    if (a === Prototype.ADMIN) {
        return -1;
    }
    if (b === Prototype.ADMIN) {
        return 1;
    }
    if (a === Prototype.EVERYONE) {
        return -1;
    }
    if (b === Prototype.EVERYONE) {
        return 1;
    }
    if (a === Prototype.OWNER) {
        return -1;
    }
    if (b === Prototype.OWNER) {
        return 1;
    }
    return 0;
}

type RolesTableProps = {
    scope: Scope;
};
export function RolesTable({ scope }: RolesTableProps) {
    const { data: { roles: globalRoles = [] } = {}, isFetching: isFetchingGlobalRoles } = useGetRolesQuery(
        Scope.GLOBAL,
    );
    const { data: { roles: rawRoles = [] } = {}, isFetching: isFetchingRoles } = useGetRolesQuery(scope);
    const isFetching = isFetchingGlobalRoles || isFetchingRoles;
    const [updateRole, { isLoading }] = useUpdateRoleMutation();
    const { t } = useTranslation();

    const roles = useMemo(() => {
        const data = [
            ...rawRoles.filter((role) => role.prototype !== Prototype.EVERYONE),
            ...globalRoles.filter((role) => role.prototype === Prototype.EVERYONE),
        ];
        data.sort(prototypePrecedence);
        return [...data];
    }, [rawRoles, globalRoles]);
    const permissions = useMemo(() => determinePermissionsForScope(scope, roles, t), [roles, scope, t]);

    const handleCheckboxChange = useCallback(
        (record: PermissionInstance, id: string, checked: boolean) => {
            const role = roles.find((role) => role.id === id);
            if (!role) {
                throw new Error('Role not found');
            }

            const permissions = [...role.permissions];
            if (checked && !permissions.includes(record.id)) {
                permissions.push(record.id);
            } else if (!checked && permissions.includes(record.id)) {
                const index = permissions.indexOf(record.id);
                permissions.splice(index, 1);
            }

            updateRole({ id: role.id, updateRole: { permissions } });
        },
        [roles, updateRole],
    );

    const renderPermission = (_: string, record: Permission) => {
        if (record.type === 'Instance') {
            return (
                <QuestionTooltip title={record.description}>
                    <Text className={styles.permissionInstance}>{record.name}</Text>
                </QuestionTooltip>
            );
        }
        if (record.type === 'Group') {
            return (
                <Text className={styles.permissionGroup} strong>
                    {record.name}
                </Text>
            );
        }
    };

    const renderCheckbox = (id: string) => (value: boolean, record: Permission) => {
        if (record.type === 'Instance') {
            const role = roles.find((role) => role.id === id);
            if (!role) {
                throw new Error('Role not found');
            }

            let checkbox: ReactElement;
            if (role.prototype === Prototype.ADMIN) {
                // Admin permissions cannot be changed
                checkbox = <Checkbox checked={true} disabled />;
            } else {
                checkbox = (
                    <Checkbox
                        checked={value}
                        onChange={(e: CheckboxChangeEvent) =>
                            handleCheckboxChange(record as PermissionInstance, id, e.target.checked)
                        }
                    />
                );
            }

            return <Flex justify="center">{checkbox}</Flex>;
        }
    };

    const createColumn = (title: string, id: string, description: string): TableColumnType<Permission> => {
        const alignToQuestionTooltip = [0, 3];
        const overlapPadding = { marginLeft: '4px', marginRight: '-20px' };

        const role = roles.find((role) => role.id === id);
        if (!role) {
            throw new Error('Role not found');
        }

        return {
            title: (
                <Space align="center" size={0}>
                    <QuestionTooltip title={description}>
                        <Text>{title}</Text>
                    </QuestionTooltip>
                    <Popover
                        placement="bottom"
                        align={{ offset: alignToQuestionTooltip }}
                        content={<RoleDetailsMenu role={role} />}
                    >
                        <Button icon={<MoreOutlined />} type="text" style={overlapPadding} />
                    </Popover>
                </Space>
            ),
            dataIndex: ['access', id],
            render: renderCheckbox(id),
        };
    };

    const roleColumns = roles.map((role) => createColumn(role.name, role.id, role.description));

    const columns: TableColumnType<Permission>[] = [
        {
            dataIndex: 'permission',
            fixed: 'left',
            className: styles.permissionsColumn,
            render: renderPermission,
            ellipsis: false,
            onCell: () => ({
                style: { whiteSpace: 'nowrap' },
            }),
        },
        ...roleColumns,
    ];

    return (
        <Flex vertical className={styles.tableContainer}>
            <Table
                columns={columns}
                loading={isFetching || isLoading}
                dataSource={permissions}
                pagination={false}
                rowKey="id"
                scroll={{ x: 'max-content' }}
            />
        </Flex>
    );
}

function determinePermissionsForScope(scope: Scope, roles: Role[], t: TFunction): Permission[] {
    let permissions: Permission[] = [];

    switch (scope) {
        case Scope.GLOBAL:
            permissions = [
                {
                    type: 'Group',
                    id: 'Manage Installation',
                    name: t('Manage Installation'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION,
                    name: t('Manage configuration'),
                    description: t('Allows modifying the configuration options of this installation'),
                },
                {
                    type: 'Group',
                    id: 'Manage Assets',
                    name: t('Manage Assets'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__CREATE_DATAPRODUCT,
                    name: t('Create Data Product'),
                    description: t('Allows the creation of a Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__CREATE_EXPLORATION,
                    name: t('Create Exploration'),
                    description: t('Allows the creation of an Exploration'),
                },
                {
                    type: 'Group',
                    id: 'Manage Access',
                    name: t('Manage Access'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__REQUEST_DATAPRODUCT_ACCESS,
                    name: t('Request Data Product access'),
                    description: t('Allows requesting access to a Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__REQUEST_OUTPUT_PORT_ACCESS,
                    name: t('Request Output Port access'),
                    description: t('Allows requesting access to an Output Port'),
                },
                {
                    type: 'Group',
                    id: 'Manage Users',
                    name: t('Manage Users'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__CREATE_USER,
                    name: t('Create User'),
                    description: t('Allows the creation of a new user'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__DELETE_USER,
                    name: t('Delete User'),
                    description: t('Allows the deletion of a user'),
                },
                {
                    type: 'Group',
                    id: 'Manage Groups',
                    name: t('Manage Groups'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__CREATE_GROUP,
                    name: t('Create Group'),
                    description: t('Allows the creation of a new group'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__UPDATE_GROUP,
                    name: t('Update Group'),
                    description: t('Allows updating fields and members of a group'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__DELETE_GROUP,
                    name: t('Delete Group'),
                    description: t('Allows deleting a group'),
                },
                {
                    type: 'Group',
                    id: 'Manage Machine Users',
                    name: t('Manage Machine Users'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__CREATE_MACHINE_USER,
                    name: t('Create Machine User'),
                    description: t('Allows the creation of a new machine user'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__UPDATE_MACHINE_USER,
                    name: t('Update Machine User'),
                    description: t('Allows updating a machine user'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__DELETE_MACHINE_USER,
                    name: t('Delete Machine User'),
                    description: t('Allows deleting a machine user'),
                },
            ];
            break;
        case Scope.DATA_PRODUCT:
            permissions = [
                {
                    type: 'Group',
                    id: 'Manage Data Product',
                    name: t('Manage Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
                    name: t('Manage general properties'),
                    description: t('Allows modifying properties such as labels and the description of a Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS,
                    name: t('Manage settings'),
                    description: t('Allows changing the settings of a Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__UPDATE_STATUS,
                    name: t('Manage status'),
                    description: t('Allows changing the status of a Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__DELETE,
                    name: t('Delete Data Product'),
                    description: t('Allows the role to delete the Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__CREATE_OUTPUT_PORT,
                    name: t('Add Output Port'),
                    description: t('Allows adding an Output Port to this Data Product'),
                },
                {
                    type: 'Group',
                    id: 'Manage Users',
                    name: t('Manage Users'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__CREATE_USER,
                    name: t('Add User'),
                    description: t('Allows adding a user as member to this Data Product and assigning a role'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__DELETE_USER,
                    name: t('Remove User'),
                    description: t('Allows removing a user as member from this Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__UPDATE_USER,
                    name: t('Modify User'),
                    description: t('Allows changing the role of a member of the Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__APPROVE_USER_REQUEST,
                    name: t('Review access request'),
                    description: t('Allows accepting or rejecting an access request made for the Data Product'),
                },
                {
                    type: 'Group',
                    id: 'Manage Technical Assets',
                    name: t('Manage Technical Assets'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__CREATE_TECHNICAL_ASSET,
                    name: t('Add Technical Asset'),
                    description: t('Allows adding a Technical Asset to this Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__DELETE_TECHNICAL_ASSET,
                    name: t('Remove and unlink Technical Asset'),
                    description: t(
                        'Allows removing a Technical Asset from this Data Product and unlinking it from a Dataset',
                    ),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET,
                    name: t('Modify Technical Asset'),
                    description: t('Allows modifying the details of a Technical Asset of this Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK,
                    name: t('Request Technical Asset Link'),
                    description: t(
                        'Allows to request that a Technical Asset of Data Product gets linked to an Output Port',
                    ),
                },
                {
                    type: 'Group',
                    id: 'Manage Input Ports',
                    name: t('Manage Input Ports'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
                    name: t('Request Access to Output Port'),
                    description: t('Allows to request read access to a Output Port'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
                    name: t('Remove Access to Output Port'),
                    description: t('Allows to remove read access to a Output Port'),
                },
                {
                    type: 'Group',
                    id: 'Integrations',
                    name: t('Integrations'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__READ_INTEGRATIONS,
                    name: t('Access Integrations'),
                    description: t('Allows the role to see and access Integrations of the Data Product'),
                },
            ];
            break;
        case Scope.DATASET:
            permissions = [
                {
                    type: 'Group',
                    id: 'Manage an Output Port',
                    name: t('Manage an Output Port'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES,
                    name: t('Manage general properties'),
                    description: t('Allows modifying properties such as labels and the description of an Output Port'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__UPDATE_SETTINGS,
                    name: t('Manage settings'),
                    description: t('Allows changing the settings of a Output Port'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__UPDATE_STATUS,
                    name: t('Manage status'),
                    description: t('Allows changing the status of a Output Port'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__DELETE,
                    name: t('Delete Output Port'),
                    description: t('Allows the role to delete the Output Port'),
                },
                {
                    type: 'Group',
                    id: 'Manage Users',
                    name: t('Manage Users'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__CREATE_USER,
                    name: t('Add User'),
                    description: t('Allows adding a user as member to this Output Port and assigning a role'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__DELETE_USER,
                    name: t('Remove User'),
                    description: t('Allows removing a user as member from this Output Port'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__UPDATE_USER,
                    name: t('Modify User'),
                    description: t('Allows changing the role of a member of the Output Port'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__APPROVE_USER_REQUEST,
                    name: t('Review access request'),
                    description: t('Allows approving or rejecting an access request made for the Output Port'),
                },
                {
                    type: 'Group',
                    id: 'Manage Technical Assets',
                    name: t('Manage Technical Assets'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST,
                    name: t('Accept Technical Asset link'),
                    description: t('Allows accepting a request to link a Technical Asset to the Output Port'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__REVOKE_TECHNICAL_ASSET_LINK,
                    name: t('Remove Technical Asset link'),
                    description: t('Allows unlinking Technical Assets from the Output Port'),
                },
                {
                    type: 'Group',
                    id: 'Manage Read Access',
                    name: t('Manage Read Access'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                    name: t('Approve Data Product Access'),
                    description: t('Allows the role to accept or reject a read access request from a Data Product'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS,
                    name: t('Revoke Data Product Access'),
                    description: t('Allows the role to revoke read access from a Data Product again'),
                },
                {
                    type: 'Group',
                    id: 'Integrations',
                    name: t('Integrations'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__READ_INTEGRATIONS,
                    name: t('Access Integrations'),
                    description: t('Allows the role to see and access Integrations of the Output Port'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__UPDATE_DATA_QUALITY,
                    name: t('Insert data quality results'),
                    description: t('Allows inserting data quality results for an Output Port'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__UPDATE_CONTRACT,
                    name: t('Manage data contract'),
                    description: t('Allows modifying the data contract of an Output Port'),
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.OUTPUT_PORT__UPDATE_QUERY_STATS,
                    name: t('Insert query statistics'),
                    description: t('Allows inserting query statistics for an Output Port'),
                },
            ];
            break;
    }

    if (scope === Scope.DATA_PRODUCT) {
        permissions.push(
            {
                type: 'Group',
                id: 'Manage Output Ports',
                name: t('Manage Output Ports'),
            },
            ...determinePermissionsForScope(Scope.DATASET, roles, t).filter(
                (permission): permission is PermissionInstance => permission.type === 'Instance',
            ),
        );
    }

    const determineAccess = (permission: AuthorizationAction) => {
        return Object.fromEntries(roles.map((role) => [role.id, role.permissions.includes(permission)]));
    };

    for (const permission of permissions) {
        if (permission.type === 'Instance') {
            permission.access = determineAccess(permission.id);
        }
    }

    return permissions;
}
