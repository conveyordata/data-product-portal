import { LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { Avatar, Badge, Flex, theme,Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { useAuth } from 'react-oidc-context';
import { useSelector } from 'react-redux';

import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';
import headerStyles from '@/components/layout/navbar/navbar.module.scss';
import { Notifications } from '@/components/notifications/notifications';
import { AppConfig } from '@/config/app-config.ts';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';

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
        <Flex className={styles.userMenuContainer}>
            <Flex>
                <Notifications />
            </Flex>
            <Flex className={styles.avatarWrapper}>
                <Badge
                    count={user?.is_admin ? t('admin') : 0}
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
                    {t('{{first_name}} {{last_name}}', {
                        first_name: user?.first_name || usernameFallback,
                        last_name: user?.last_name || usernameFallback,
                    })}
                </Typography.Text>
            </Flex>
            <Flex className={headerStyles.headerActionsWrapper}>
                <CircleIconButton
                    icon={<LogoutOutlined rotate={270} />}
                    tooltip={t('Logout')}
                    onClick={handleLogout}
                    buttonProps={{ disabled: isAuthDisabled }}
                />
            </Flex>
        </Flex>
    );
}
