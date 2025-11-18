import { CrownOutlined, UserSwitchOutlined } from '@ant-design/icons';
import { Button, Popover } from 'antd';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import {
    useCreateGlobalRoleAssignmentMutation,
    useDecideGlobalRoleAssignmentMutation,
    useDeleteGlobalRoleAssignmentMutation,
    useGetGlobalRoleAssignmentsQuery,
} from '@/store/features/role-assignments/global-roles-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import styles from './admin-button.module.scss';

type Props = {
    onAdminAction?: () => void;
    isAdmin?: boolean;
};

export function AdminButton({ onAdminAction, isAdmin }: Props) {
    const { t } = useTranslation();
    const [createGlobalRoleAssignment] = useCreateGlobalRoleAssignmentMutation();
    const [decideGlobalRoleAssignment] = useDecideGlobalRoleAssignmentMutation();
    const { data: globalRoleAssignments } = useGetGlobalRoleAssignmentsQuery({
        user_id: useSelector(selectCurrentUser)?.id || '',
        role_id: '00000000-0000-0000-0000-000000000000',
        decision: 'approved',
    });
    const [deleteGlobalRoleAssignment] = useDeleteGlobalRoleAssignmentMutation();
    const currentUser = useSelector(selectCurrentUser);

    const { data: become_admin_access } = useCheckAccessQuery({
        action: AuthorizationAction.GLOBAL__CREATE_USER,
    });

    const canBecomeAdmin = become_admin_access?.allowed ?? false;

    if (!currentUser || !canBecomeAdmin) return null;

    const handleAdminAction = async () => {
        if (globalRoleAssignments && globalRoleAssignments.length > 0) {
            // Revoke admin access
            await deleteGlobalRoleAssignment({ role_assignment_id: globalRoleAssignments[0].id });

            onAdminAction?.();
            return;
        }
        const expiry = new Date();
        expiry.setMinutes(expiry.getMinutes() + 1); // expire 1 minute from now
        const result = await createGlobalRoleAssignment({
            role_id: '00000000-0000-0000-0000-000000000000',
            user_id: currentUser.id,
            expiry: expiry.toISOString(),
        }).unwrap();
        await decideGlobalRoleAssignment({ role_assignment_id: result.id, decision_status: 'approved' });

        onAdminAction?.();
    };

    return (
        <Popover
            content={isAdmin ? t('Remove admin privileges') : t('Gain temporary admin privileges')}
            trigger={'hover'}
            placement="bottom"
        >
            <Button
                shape={'circle'}
                className={styles.iconButton}
                icon={isAdmin ? <UserSwitchOutlined /> : <CrownOutlined />}
                onClick={handleAdminAction}
            />
        </Popover>
    );
}
