import { LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { Avatar, Badge, Flex, Typography, theme } from 'antd';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from 'react-oidc-context';
import { useSelector } from 'react-redux';

import { AdminButton } from '@/components/buttons/admin-button.tsx';
import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';
import { CartButton } from '@/components/cart/cart-button.component.tsx';
import { Notifications } from '@/components/notifications/notifications';
import { AppConfig } from '@/config/app-config.ts';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useIsAdminQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useRevokeAdminMutation } from '@/store/features/role-assignments/global-roles-api-slice';
import { DownloadCLIButton } from '../cli-download/cli-download-button.component';
import styles from './user-menu.module.scss';

const cognitoLogoutParams = AppConfig.getOidcCognitoLogoutParams();
const isAuthDisabled = !AppConfig.isOidcEnabled();

export function UserMenu() {
    const { t } = useTranslation();
    const usernameFallback = t('User');
    const { signoutRedirect } = useAuth();
    const user = useSelector(selectCurrentUser);
    const {
        token: { colorErrorBorder, colorPrimary },
    } = theme.useToken();
    const userInitials = user?.first_name?.charAt(0) + (user?.last_name ? user.last_name.charAt(0) : '');
    const [revokeAdmin] = useRevokeAdminMutation();
    const [timeRemaining, setTimeRemaining] = useState<string>('');

    const { data: isAdmin } = useIsAdminQuery();

    useEffect(() => {
        if (!isAdmin?.is_admin || !isAdmin?.time) {
            setTimeRemaining('');
            return;
        }

        const updateTimeRemaining = async () => {
            const expiry = new Date(`${isAdmin.time}Z`).getTime(); // UTC → epoch ms
            const now = Date.now();
            const diff = expiry - now;

            if (diff <= 0) {
                setTimeRemaining('expired');
                if (user) {
                    await revokeAdmin({ user_id: user.id }).unwrap();
                }
                window.location.reload(); // Refetch to update admin status
                return;
            }

            const minutes = Math.floor(diff / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);

            if (minutes < 1) {
                setTimeRemaining(`${seconds}s`);
            } else {
                setTimeRemaining(`${minutes}m`);
            }
        };

        updateTimeRemaining();
        const interval = setInterval(updateTimeRemaining, 1000);

        return () => clearInterval(interval);
    }, [isAdmin, user, revokeAdmin]);

    const handleLogout = async () => {
        if (isAuthDisabled) {
            return;
        }

        try {
            await signoutRedirect({
                // For Cognito logout we need to pass extra query params otherwise the redirect will always fail
                extraQueryParams: {
                    ...cognitoLogoutParams,
                },
            });
        } catch (e) {
            console.error('Failed to logout', e);
        }
    };

    return (
        <Flex gap={'middle'} align={'center'}>
            <Notifications />
            <CartButton />
            <DownloadCLIButton />
            <AdminButton onAdminAction={() => window.location.reload()} isAdmin={isAdmin?.is_admin} />
            <Flex align={'center'} gap={'small'}>
                <Badge
                    count={isAdmin?.is_admin ? (timeRemaining ? t('admin for ') + timeRemaining : t('admin')) : 0}
                    showZero={false}
                    color={colorPrimary}
                    style={{ fontSize: 10 }}
                    size="small"
                >
                    <Avatar style={{ backgroundColor: colorErrorBorder }} className={styles.avatar}>
                        {userInitials || <UserOutlined />}
                    </Avatar>
                </Badge>

                <Typography.Text strong className={styles.userGreeting}>
                    {user?.first_name || usernameFallback} {user?.last_name || usernameFallback}
                </Typography.Text>
            </Flex>
            <CircleIconButton
                icon={<LogoutOutlined rotate={270} />}
                tooltip={t('Logout')}
                onClick={handleLogout}
                buttonProps={{ disabled: isAuthDisabled }}
            />
        </Flex>
    );
}
