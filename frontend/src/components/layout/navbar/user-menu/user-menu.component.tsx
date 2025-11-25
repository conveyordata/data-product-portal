import { LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { Avatar, Badge, Dropdown, Flex, type MenuProps, Typography, theme } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from 'react-oidc-context';
import { useSelector } from 'react-redux';

import { AdminButton } from '@/components/buttons/admin-button.tsx';
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
type MenuItem = Required<MenuProps>['items'][number];
const { Text } = Typography;

export function UserMenu() {
    const { t } = useTranslation();
    const { signoutRedirect } = useAuth();
    const user = useSelector(selectCurrentUser);
    const {
        token: { colorErrorBorder, colorPrimary },
    } = theme.useToken();
    const userInitials = user?.first_name?.charAt(0) + (user?.last_name ? user.last_name.charAt(0) : '');
    const [revokeAdmin] = useRevokeAdminMutation();

    const { data: isAdmin } = useIsAdminQuery();

    useEffect(() => {
        if (!isAdmin?.is_admin || !isAdmin?.time) {
            return;
        }

        const reload_when_admin_expires = async () => {
            const expiry = new Date(`${isAdmin.time}Z`).getTime(); // UTC → epoch ms
            const now = Date.now();
            const diff = expiry - now;

            if (diff <= 0) {
                if (user) {
                    await revokeAdmin({ user_id: user.id }).unwrap();
                }
                window.location.reload(); // Refetch to update admin status
                return;
            }
        };

        reload_when_admin_expires();
        const interval = setInterval(reload_when_admin_expires, 1000);

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

    const userItem = (): MenuItem => ({
        key: 'UserInfo',
        icon: <UserOutlined style={{ cursor: 'default' }} />,
        style: { cursor: 'default' },
        label: (
            <Text
                style={{ maxWidth: '20em' }}
                ellipsis={{
                    tooltip: {
                        title: user?.first_name + ' ' + user?.last_name,
                        styles: { root: { maxWidth: 'fit-content' } },
                    },
                }}
            >
                {user?.first_name} {user?.last_name}
            </Text>
        ),
    });

    const signOutItem: MenuItem = {
        key: 'SignOut',
        icon: <LogoutOutlined />,
        label: t('Sign out'),
        onClick: handleLogout,
    };

    const items = [
        userItem(),
        AdminButton({ onAdminAction: () => window.location.reload(), isAdmin: isAdmin?.is_admin }),
        signOutItem,
    ];

    return (
        <Flex gap={'middle'} align={'center'}>
            <Notifications />
            <CartButton />
            <DownloadCLIButton />
            <Flex align={'center'} gap={'small'}>
                <Dropdown
                    menu={{ items }}
                    placement={'bottomRight'}
                    arrow={{ pointAtCenter: true }}
                    mouseLeaveDelay={0.3}
                >
                    {
                        <Badge
                            count={
                                isAdmin?.is_admin
                                    ? t('Admin powers until ') +
                                      new Date(`${isAdmin?.time}Z`).toLocaleTimeString(undefined, {
                                          hour: '2-digit',
                                          minute: '2-digit',
                                      })
                                    : 0
                            }
                            showZero={false}
                            color={colorPrimary}
                            style={{ fontSize: 10 }}
                            size="small"
                            offset={[-50, 0]}
                        >
                            <Avatar style={{ backgroundColor: colorErrorBorder }} className={styles.avatar}>
                                {userInitials || <UserOutlined />}
                            </Avatar>
                        </Badge>
                    }
                </Dropdown>
            </Flex>
        </Flex>
    );
}
