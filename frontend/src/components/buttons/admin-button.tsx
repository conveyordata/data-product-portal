import { CrownOutlined, UserSwitchOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import type { MenuProps } from 'antd';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { PosthogEvents } from '@/constants/posthog.constants';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import {
    useBecomeAdminMutation,
    useRevokeAdminMutation,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';

type Props = {
    onAdminAction?: () => void;
    isAdmin?: boolean;
};

export function AdminButton({ onAdminAction, isAdmin }: Props): Required<MenuProps>['items'][number] {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const [becomeAdmin] = useBecomeAdminMutation();
    const [revokeAdmin] = useRevokeAdminMutation();
    const currentUser = useSelector(selectCurrentUser);

    const canBecomeAdmin = currentUser?.can_become_admin ?? false;

    if (!currentUser || !canBecomeAdmin) return null;

    const handleAdminAction = async () => {
        if (isAdmin) {
            posthog.capture(PosthogEvents.ADMIN_PRIVILEGES_REVOKED);
            // Revoke admin access
            await revokeAdmin().unwrap();

            onAdminAction?.();
            return;
        }
        posthog.capture(PosthogEvents.ADMIN_PRIVILEGES_GRANTED);
        const expiry = new Date();
        expiry.setMinutes(expiry.getMinutes() + 10); // expire 10 minutes from now
        await becomeAdmin({
            expiry: expiry.toISOString(),
        }).unwrap();
        onAdminAction?.();
    };

    return {
        key: 'BecomeAdmin',
        icon: isAdmin ? <UserSwitchOutlined /> : <CrownOutlined />,
        label: isAdmin ? t('Remove admin privileges') : t('Gain temporary admin privileges'),
        onClick: handleAdminAction,
    };
}
