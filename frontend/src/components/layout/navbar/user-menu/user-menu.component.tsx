import { Avatar, Flex, theme, Typography } from 'antd';
import styles from '@/components/layout/navbar/navbar.module.scss';
import { LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';
import { useAuth } from 'react-oidc-context';
import { AppConfig } from '@/config/app-config.ts';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';

const cognitoLogoutParams = AppConfig.getOidcCognitoLogoutParams();
const isAuthDisabled = AppConfig.isOidcDisabled();

export function UserMenu() {
    const { t } = useTranslation();
    const usernameFallback = t('User');
    const { signoutRedirect } = useAuth();
    const user = useSelector(selectCurrentUser);
    const {
        token: { colorErrorBorder },
    } = theme.useToken();
    const userInitials = user?.first_name && user.first_name.charAt(0);

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
            <Flex className={styles.avatarWrapper}>
                <Avatar style={{ backgroundColor: colorErrorBorder }} className={styles.avatar}>
                    {userInitials || <UserOutlined />}
                </Avatar>
                <Typography.Text strong className={styles.userGreeting}>
                    {t('Hello, {{name}}', { name: user?.first_name || usernameFallback })}
                </Typography.Text>
            </Flex>
            <Flex className={styles.headerActionsWrapper}>
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
