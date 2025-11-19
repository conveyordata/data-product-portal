import { CrownOutlined, UserSwitchOutlined } from '@ant-design/icons';
import { Button, Popover } from 'antd';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import {
    useBecomeAdminMutation,
    useRevokeAdminMutation,
} from '@/store/features/role-assignments/global-roles-api-slice';
import styles from './admin-button.module.scss';

type Props = {
    onAdminAction?: () => void;
    isAdmin?: boolean;
};

export function AdminButton({ onAdminAction, isAdmin }: Props) {
    const { t } = useTranslation();
    const [becomeAdmin] = useBecomeAdminMutation();
    const [revokeAdmin] = useRevokeAdminMutation();
    const currentUser = useSelector(selectCurrentUser);

    const canBecomeAdmin = currentUser?.can_become_admin ?? false;

    if (!currentUser || !canBecomeAdmin) return null;

    const handleAdminAction = async () => {
        if (isAdmin) {
            // Revoke admin access
            await revokeAdmin({ user_id: currentUser.id }).unwrap();

            onAdminAction?.();
            return;
        }
        const expiry = new Date();
        expiry.setMinutes(expiry.getMinutes() + 10); // expire 10 minutes from now
        await becomeAdmin({
            user_id: currentUser.id,
            expiry: expiry.toISOString(),
        }).unwrap();
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
