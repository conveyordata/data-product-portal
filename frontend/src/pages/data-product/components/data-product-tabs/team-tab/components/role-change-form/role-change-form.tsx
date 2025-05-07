import { Form, FormProps, Select } from 'antd';

import { useGetRolesQuery } from '@/store/features/roles/roles-api-slice';
import { RoleContract } from '@/types/roles';
import { RoleAssignmentContract } from '@/types/roles/role.contract';

import styles from './role-change-form.module.scss';

type Props = {
    userId: string;
    initialRole: RoleContract;
    dataProductUsers: RoleAssignmentContract[];
    onRoleChange: (role: RoleContract) => void;
    isDisabled?: boolean;
};

export function RoleChangeForm({ userId, initialRole, onRoleChange, isDisabled = true }: Props) {
    const [dataProductRoleForm] = Form.useForm<RoleAssignmentContract>();
    const { data: DATA_PRODUCT_ROLES, isLoading } = useGetRolesQuery('data_product', { skip: isDisabled });
    // const DATA_PRODUCT_ROLES = getRoleOptions(t);

    const handleRoleChange: FormProps<RoleContract>['onFinish'] = (role) => {
        console.log(role);
        if (role !== initialRole) {
            onRoleChange(role);
        }
    };
    return (
        <Form<RoleAssignmentContract>
            form={dataProductRoleForm}
            initialValues={{ role: initialRole.name }}
            disabled={isDisabled}
        >
            <Form.Item<RoleAssignmentContract> name={'role'} className={styles.selectRoleWrapper}>
                <Select
                    loading={isLoading}
                    onSelect={(roleName: string) => {
                        const selectedRole = DATA_PRODUCT_ROLES?.find((role) => role.name === roleName);
                        if (selectedRole) {
                            handleRoleChange(selectedRole);
                        }
                    }}
                >
                    {DATA_PRODUCT_ROLES?.map((role) => (
                        <Select.Option key={`${role.name}-${userId}`} value={role.name}>
                            {role.name}
                        </Select.Option>
                    ))}
                </Select>
            </Form.Item>
        </Form>
    );
}
