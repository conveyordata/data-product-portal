import { SafetyCertificateOutlined } from '@ant-design/icons';
import { Form, Modal, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import { EmptyState, hasFailed } from '@/components/empty-state/empty-state.component.tsx';
import { IdentityAvatarWithDetails } from '@/components/identity-avatar/identity-avatar.component.tsx';
import { IdentitySelector } from '@/components/identity-selector/identity-selector.component.tsx';
import { RoleChangeForm } from '@/components/roles/role-change-form/role-change-form.tsx';
import {
    type UserIdentity,
    useCreateDataProductRoleAssignmentMutation,
    useListDataProductRoleAssignmentsQuery,
    useRequestDataProductRoleAssignmentMutation,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import { useGetRolesQuery } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { DecisionStatus, Prototype, Scope } from '@/types/roles';
import { dispatchMessage } from '@/utils/feedback.ts';
import { getIdentityDisplayName, type Identity } from '@/utils/identity.ts';

type Props = {
    dataProductId: string;
    onClose: () => void;
} & ({ mode: 'assign'; initialIdentity?: never } | { mode: 'request'; initialIdentity: UserIdentity });

type Values = { roleId: string };

export function DataProductRoleModal({ dataProductId, mode, initialIdentity, onClose }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm<Values>();
    const rolesQuery = useGetRolesQuery(Scope.DATA_PRODUCT);
    const assignmentsQuery = useListDataProductRoleAssignmentsQuery({ dataProductId });
    const [assignRole, { isLoading: isAssigning }] = useCreateDataProductRoleAssignmentMutation();
    const [requestRole, { isLoading: isRequesting }] = useRequestDataProductRoleAssignmentMutation();
    const isSubmitting = isAssigning || isRequesting;
    const loadFailed = hasFailed(rolesQuery) || hasFailed(assignmentsQuery);
    const isReady =
        !loadFailed &&
        !assignmentsQuery.isFetching &&
        !!rolesQuery.currentData?.roles.length &&
        !!assignmentsQuery.currentData;
    const assignedIdentityIds = (assignmentsQuery.currentData?.role_assignments ?? [])
        .filter((assignment) => assignment.decision !== DecisionStatus.Denied)
        .map((assignment) => assignment.identity.id);
    const handleSubmit = async (identity: Identity, roleId: string) => {
        const role = rolesQuery.currentData?.roles.find((role) => role.id === roleId);
        if (identity.type !== 'user' && role?.prototype === Prototype.OWNER) {
            dispatchMessage({ content: t('Only users can be Data Product owners'), type: 'error' });
            return;
        }
        try {
            const submit = mode === 'assign' ? assignRole : requestRole;
            const assignment = await submit({
                data_product_id: dataProductId,
                identity_id: identity.id,
                role_id: roleId,
            }).unwrap();
            dispatchMessage({
                content:
                    assignment.decision === DecisionStatus.Approved
                        ? t('Role has been assigned')
                        : t('Role request has been submitted'),
                type: 'success',
            });
            if (mode === 'request') onClose();
        } catch {
            dispatchMessage({
                content: mode === 'assign' ? t('Failed to assign role') : t('Failed to request role'),
                type: 'error',
            });
        }
    };

    return (
        <Modal
            open
            title={mode === 'assign' ? t('Add team member') : t('Request Data Product role')}
            width={{ xs: '95%', md: '80%', lg: '60%' }}
            onCancel={onClose}
            onOk={() => form.submit()}
            footer={mode === 'assign' ? (_, { CancelBtn }) => <CancelBtn /> : undefined}
            okText={t('Request role')}
            okButtonProps={{ disabled: !isReady }}
            confirmLoading={isSubmitting}
            cancelButtonProps={{ disabled: isSubmitting }}
        >
            {loadFailed ? (
                <EmptyState
                    icon={<SafetyCertificateOutlined />}
                    title={t('No roles available')}
                    subject={t('role assignments')}
                    error
                    onRetry={() => {
                        rolesQuery.refetch();
                        assignmentsQuery.refetch();
                    }}
                />
            ) : mode === 'assign' ? (
                <IdentitySelector
                    identityIdsToHide={assignedIdentityIds}
                    disabled={isSubmitting || !isReady}
                    renderAction={(identity, disabled) => (
                        <RoleChangeForm
                            scope={Scope.DATA_PRODUCT}
                            ariaLabel={t('Assign role to {{name}}', { name: getIdentityDisplayName(identity) })}
                            placeholder={t('Select a role')}
                            allowOwner={identity.type === 'user'}
                            disabled={disabled}
                            onRoleChange={(role) => handleSubmit(identity, role.id)}
                        />
                    )}
                />
            ) : (
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={({ roleId }: Values) => handleSubmit(initialIdentity, roleId)}
                    disabled={isSubmitting}
                >
                    <Form.Item label={t('Identity')} required>
                        <IdentityAvatarWithDetails identity={initialIdentity} />
                    </Form.Item>
                    <Form.Item<Values>
                        label={t('Role')}
                        name="roleId"
                        rules={[{ required: true, message: t('Please select a role') }]}
                    >
                        <Select
                            loading={rolesQuery.isFetching}
                            disabled={isSubmitting || !isReady}
                            options={rolesQuery.currentData?.roles.map((role) => ({
                                value: role.id,
                                label: role.name,
                            }))}
                            notFoundContent={t('No roles available')}
                        />
                    </Form.Item>
                </Form>
            )}
        </Modal>
    );
}
