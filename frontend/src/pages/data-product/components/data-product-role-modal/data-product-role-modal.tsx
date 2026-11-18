import { SafetyCertificateOutlined } from '@ant-design/icons';
import { Button, Flex, Form, Modal, Select } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { EmptyState, hasFailed } from '@/components/empty-state/empty-state.component.tsx';
import { IdentityAvatarWithDetails } from '@/components/identity-avatar/identity-avatar.component.tsx';
import { IdentitySelector } from '@/components/identity-selector/identity-selector.component.tsx';
import {
    type UserIdentity,
    useCreateDataProductRoleAssignmentMutation,
    useListDataProductRoleAssignmentsQuery,
    useRequestDataProductRoleAssignmentMutation,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import { useGetRolesQuery } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { DecisionStatus, Prototype, Scope } from '@/types/roles';
import { dispatchMessage } from '@/utils/feedback.ts';
import { IDENTITY_TYPES, type Identity } from '@/utils/identity.ts';

type Props = {
    dataProductId: string;
    onClose: () => void;
} & ({ mode: 'assign'; initialIdentity?: never } | { mode: 'request'; initialIdentity: UserIdentity });

type Values = { roleId: string };

export function DataProductRoleModal({ dataProductId, mode, initialIdentity, onClose }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm<Values>();
    const [selectedIdentity, setSelectedIdentity] = useState<Identity>();
    const [identityTypes, setIdentityTypes] = useState(IDENTITY_TYPES);
    const identity = mode === 'request' ? initialIdentity : selectedIdentity;
    const rolesQuery = useGetRolesQuery(Scope.DATA_PRODUCT);
    const assignmentsQuery = useListDataProductRoleAssignmentsQuery({ dataProductId });
    const [assignRole, { isLoading: isAssigning }] = useCreateDataProductRoleAssignmentMutation();
    const [requestRole, { isLoading: isRequesting }] = useRequestDataProductRoleAssignmentMutation();
    const isSubmitting = isAssigning || isRequesting;
    const loadFailed = hasFailed(rolesQuery) || hasFailed(assignmentsQuery);
    const isReady = !loadFailed && !!rolesQuery.currentData?.roles.length && !!assignmentsQuery.currentData;
    const assignedIdentityIds = (assignmentsQuery.currentData?.role_assignments ?? [])
        .filter((assignment) => assignment.decision !== DecisionStatus.Denied)
        .map((assignment) => assignment.identity.id);
    const allowOwner = !identity || identity.type === 'user';
    const getSelectedRole = () =>
        rolesQuery.currentData?.roles.find((role) => role.id === form.getFieldValue('roleId'));

    const handleIdentityChange = (nextIdentity?: Identity) => {
        setSelectedIdentity(nextIdentity);
        if (nextIdentity && nextIdentity.type !== 'user' && getSelectedRole()?.prototype === Prototype.OWNER) {
            form.setFieldValue('roleId', undefined);
        }
    };

    const handleSubmit = async ({ roleId }: Values) => {
        if (!identity) {
            dispatchMessage({ content: t('Please select an identity'), type: 'error' });
            return;
        }
        if (!allowOwner && getSelectedRole()?.prototype === Prototype.OWNER) {
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
            onClose();
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
            okText={mode === 'assign' ? t('Assign role') : t('Request role')}
            okButtonProps={{ disabled: !identity || !isReady }}
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
            ) : (
                <Form form={form} layout="vertical" onFinish={handleSubmit} disabled={isSubmitting}>
                    <Form.Item label={identity ? t('Identity') : undefined} required={!!identity}>
                        {identity ? (
                            <Flex align="center" justify="space-between" gap="small">
                                <IdentityAvatarWithDetails identity={identity} />
                                {mode === 'assign' && (
                                    <Button type="link" onClick={() => handleIdentityChange()} disabled={isSubmitting}>
                                        {t('Change identity')}
                                    </Button>
                                )}
                            </Flex>
                        ) : (
                            <IdentitySelector
                                onSelect={handleIdentityChange}
                                identityTypes={identityTypes}
                                onIdentityTypesChange={setIdentityTypes}
                                identityIdsToHide={assignedIdentityIds}
                                disabled={isSubmitting || !isReady}
                            />
                        )}
                    </Form.Item>
                    <Form.Item<Values>
                        label={t('Role')}
                        name="roleId"
                        rules={[{ required: true, message: t('Please select a role') }]}
                        extra={identity && !allowOwner ? t('Only users can be Data Product owners') : undefined}
                    >
                        <Select
                            loading={rolesQuery.isFetching}
                            disabled={isSubmitting || !isReady}
                            onChange={(roleId) => {
                                if (
                                    rolesQuery.currentData?.roles.find((role) => role.id === roleId)?.prototype ===
                                    Prototype.OWNER
                                ) {
                                    setIdentityTypes((types) => types.filter((type) => type === 'user'));
                                }
                            }}
                            options={rolesQuery.currentData?.roles.map((role) => ({
                                value: role.id,
                                label: role.name,
                                disabled: !allowOwner && role.prototype === Prototype.OWNER,
                            }))}
                            notFoundContent={t('No roles available')}
                        />
                    </Form.Item>
                </Form>
            )}
        </Modal>
    );
}
