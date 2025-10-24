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
import { type ReactElement, useCallback, useMemo } from 'react';
import QuestionTooltip from '@/components/tooltip/question-tooltip';
import { RoleDetailsMenu } from '@/pages/roles/components/role-details-menu.component.tsx';
import { useGetRolesQuery, useUpdateRoleMutation } from '@/store/features/roles/roles-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import type { RoleContract } from '@/types/roles';
import { Prototype, Scope } from '@/types/roles';
import styles from './roles-table.module.scss';

const { Text } = Typography;

type PermissionType = 'Group' | 'Instance';

type PermissionBase = {
    type: PermissionType;
    id: number | string;
    name: string;
};

type PermissionInstance = PermissionBase & {
    type: 'Instance';
    id: number;
    description: string;
    access?: object;
};

type PermissionGroup = PermissionBase & {
    type: 'Group';
    id: string;
};

type Permission = PermissionInstance | PermissionGroup;

function prototypePrecedence(role_a: RoleContract, role_b: RoleContract) {
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
    const { data: globalRoles = [], isFetching: isFetchingGlobalRoles } = useGetRolesQuery(Scope.GLOBAL);
    const { data: rawRoles = [], isFetching: isFetchingRoles } = useGetRolesQuery(scope);
    const isFetching = isFetchingGlobalRoles || isFetchingRoles;
    const [updateRole, { isLoading }] = useUpdateRoleMutation();

    const roles = useMemo(() => {
        const data = [
            ...rawRoles.filter((role) => role.prototype !== Prototype.EVERYONE),
            ...globalRoles.filter((role) => role.prototype === Prototype.EVERYONE),
        ];
        data.sort(prototypePrecedence);
        return [...data];
    }, [rawRoles, globalRoles]);
    const permissions = useMemo(() => determinePermissionsForScope(scope, roles), [roles, scope]);

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

            updateRole({ id: role.id, permissions });
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

            return <Flex justify={'center'}>{checkbox}</Flex>;
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
                <Space align={'center'} size={0}>
                    <QuestionTooltip title={description}>
                        <Text>{title}</Text>
                    </QuestionTooltip>
                    <Popover
                        placement={'bottom'}
                        align={{ offset: alignToQuestionTooltip }}
                        content={<RoleDetailsMenu role={role} />}
                    >
                        <Button icon={<MoreOutlined />} type={'text'} style={overlapPadding} />
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
                rowKey={'id'}
                scroll={{ x: 'max-content' }}
            />
        </Flex>
    );
}

function determinePermissionsForScope(scope: Scope, roles: RoleContract[]): Permission[] {
    let permissions: Permission[] = [];

    switch (scope) {
        case Scope.GLOBAL:
            permissions = [
                {
                    type: 'Group',
                    id: 'Manage Installation',
                    name: 'Manage Installation',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION,
                    name: 'Manage configuration',
                    description: 'Allows modifying the configuration options of this installation',
                },
                {
                    type: 'Group',
                    id: 'Manage Assets',
                    name: 'Manage Assets',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__CREATE_DATAPRODUCT,
                    name: 'Create Data Product',
                    description: 'Allows the creation of a Data Product',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__CREATE_DATASET,
                    name: 'Create Dataset',
                    description: 'Allows the creation of a Dataset',
                },
                {
                    type: 'Group',
                    id: 'Manage Access',
                    name: 'Manage Access',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__REQUEST_DATAPRODUCT_ACCESS,
                    name: 'Request Data Product access',
                    description: 'Allows requesting access to a Data Product',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__REQUEST_DATASET_ACCESS,
                    name: 'Request Dataset access',
                    description: 'Allows requesting access to a Dataset',
                },
                {
                    type: 'Group',
                    id: 'Manage Users',
                    name: 'Manage Users',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__CREATE_USER,
                    name: 'Create User',
                    description: 'Allows the creation of a new user',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.GLOBAL__DELETE_USER,
                    name: 'Delete User',
                    description: 'Allows the deletion of a user',
                },
            ];
            break;
        case Scope.DATA_PRODUCT:
            permissions = [
                {
                    type: 'Group',
                    id: 'Manage Data Product',
                    name: 'Manage Data Product',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
                    name: 'Manage general properties',
                    description: 'Allows modifying properties such as labels and the description of a Data Product',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS,
                    name: 'Manage settings',
                    description: 'Allows changing the settings of a Data Product',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__UPDATE_STATUS,
                    name: 'Manage status',
                    description: 'Allows changing the status of a Data Product',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__DELETE,
                    name: 'Delete Data Product',
                    description: 'Allows the role to delete the Data Product',
                },
                {
                    type: 'Group',
                    id: 'Manage Users',
                    name: 'Manage Users',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__CREATE_USER,
                    name: 'Add User',
                    description: 'Allows adding a user as member to this Data Product and assigning a role',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__DELETE_USER,
                    name: 'Remove User',
                    description: 'Allows removing a user as member from this Data Product',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__UPDATE_USER,
                    name: 'Modify User',
                    description: 'Allows changing the role of a member of the Data Product',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__APPROVE_USER_REQUEST,
                    name: 'Review access request',
                    description: 'Allows accepting or rejecting an access request made for the Data Product',
                },
                {
                    type: 'Group',
                    id: 'Manage Technical Assets',
                    name: 'Manage Technical Assets',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__CREATE_DATA_OUTPUT,
                    name: 'Add Technical Asset',
                    description: 'Allows adding a Technical Asset to this Data Product',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__DELETE_DATA_OUTPUT,
                    name: 'Remove and unlink Technical Asset',
                    description:
                        'Allows removing a Technical Asset from this Data Product and unlinking it from a Dataset',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__UPDATE_DATA_OUTPUT,
                    name: 'Modify Technical Asset',
                    description: 'Allows modifying the details of a Technical Asset of this Data Product',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
                    name: 'Request Technical Asset Link',
                    description: 'Allows to request that a Technical Asset of Data Product gets linked to a Dataset',
                },
                {
                    type: 'Group',
                    id: 'Manage Input Datasets',
                    name: 'Manage Input Datasets',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__REQUEST_DATASET_ACCESS,
                    name: 'Request Access to Dataset',
                    description: 'Allows to request read access to a Dataset',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
                    name: 'Remove Access to Dataset',
                    description: 'Allows to remove read access to a Dataset',
                },
                {
                    type: 'Group',
                    id: 'Integrations',
                    name: 'Integrations',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATA_PRODUCT__READ_INTEGRATIONS,
                    name: 'Access Integrations',
                    description: 'Allows the role to see and access Integrations of the Data Product',
                },
            ];
            break;
        case Scope.DATASET:
            permissions = [
                {
                    type: 'Group',
                    id: 'Manage Dataset',
                    name: 'Manage Dataset',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__UPDATE_PROPERTIES,
                    name: 'Manage general properties',
                    description: 'Allows modifying properties such as labels and the description of a Dataset',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__UPDATE_SETTINGS,
                    name: 'Manage settings',
                    description: 'Allows changing the settings of a Dataset',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__UPDATE_STATUS,
                    name: 'Manage status',
                    description: 'Allows changing the status of a Dataset',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__DELETE,
                    name: 'Delete Dataset',
                    description: 'Allows the role to delete the Dataset',
                },
                {
                    type: 'Group',
                    id: 'Manage Users',
                    name: 'Manage Users',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__CREATE_USER,
                    name: 'Add User',
                    description: 'Allows adding a user as member to this Dataset and assigning a role',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__DELETE_USER,
                    name: 'Remove User',
                    description: 'Allows removing a user as member from this Dataset',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__UPDATE_USER,
                    name: 'Modify User',
                    description: 'Allows changing the role of a member of the Dataset',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__APPROVE_USER_REQUEST,
                    name: 'Review access request',
                    description: 'Allows approving or rejecting an access request made for the Dataset',
                },
                {
                    type: 'Group',
                    id: 'Manage Technical Assets',
                    name: 'Manage Technical Assets',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
                    name: 'Accept Technical Asset link',
                    description: 'Allows accepting a request to link a Technical Asset to the Dataset',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__REVOKE_DATA_OUTPUT_LINK,
                    name: 'Remove Technical Asset link',
                    description: 'Allows unlinking Technical Assets from the Dataset',
                },
                {
                    type: 'Group',
                    id: 'Manage Read Access',
                    name: 'Manage Read Access',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                    name: 'Approve Data Product Access',
                    description: 'Allows the role to accept or reject a read access request from a data product',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__REVOKE_DATAPRODUCT_ACCESS,
                    name: 'Revoke Data Product Access',
                    description: 'Allows the role to revoke read access from a data product again',
                },
                {
                    type: 'Group',
                    id: 'Integrations',
                    name: 'Integrations',
                },
                {
                    type: 'Instance',
                    id: AuthorizationAction.DATASET__READ_INTEGRATIONS,
                    name: 'Access Integrations',
                    description: 'Allows the role to see and access Integrations of the Dataset',
                },
            ];
            break;
    }

    const determineAccess = (permission: number) => {
        return Object.fromEntries(roles.map((role) => [role.id, role.permissions.includes(permission)]));
    };

    for (const permission of permissions) {
        if (permission.type === 'Instance') {
            permission.access = determineAccess(permission.id);
        }
    }

    return permissions;
}
