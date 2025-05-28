import { Form, type FormProps, Select } from 'antd';

import { useGetRolesQuery } from '@/store/features/roles/roles-api-slice';
import type { RoleContract } from '@/types/roles';

import styles from './role-change-form.module.scss';

interface RoleAssignment {
    role: RoleContract;
}

type Props = {
    userId: string;
    initialRole: RoleContract;
    onRoleChange: (role: RoleContract) => void;
    isDisabled?: boolean;
    scope: 'data_product' | 'dataset';
};
export function RoleChangeForm<Type extends RoleAssignment>({
    userId,
    initialRole,
    onRoleChange,
    isDisabled = true,
    scope,
}: Props) {
    const [dataProductRoleForm] = Form.useForm<Type>();
    const { data: ROLES, isLoading } = useGetRolesQuery(scope, { skip: isDisabled });

    const handleRoleChange: FormProps<RoleContract>['onFinish'] = (role) => {
        console.log(role);
        if (role !== initialRole) {
            onRoleChange(role);
        }
    };

    return (
        <Form<Type> form={dataProductRoleForm} initialValues={{ role: initialRole.name }} disabled={isDisabled}>
            <Form.Item<RoleAssignment> name={'role'} className={styles.selectRoleWrapper}>
                <Select
                    loading={isLoading}
                    onSelect={(roleName: string) => {
                        const selectedRole = ROLES?.find((role) => role.name === roleName);
                        if (selectedRole) {
                            handleRoleChange(selectedRole);
                        }
                    }}
                >
                    {ROLES?.map((role) => (
                        <Select.Option key={`${role.name}-${userId}`} value={role.name}>
                            {role.name}
                        </Select.Option>
                    ))}
                </Select>
            </Form.Item>
        </Form>
    );
}
