import { useAuth } from 'react-oidc-context';
import { Button, Flex, Result, Typography, Watermark } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './logout.module.scss';
import { ArrowRightOutlined } from '@ant-design/icons';
import { LogoText } from '@/components/branding/logo/logo-text.tsx';

export function Logout() {
    const { t } = useTranslation();
    const { signinRedirect, isLoading } = useAuth();

    async function handleSigninRedirect() {
        await signinRedirect();
    }

    return (
        <>
            <Watermark content={t('Logo')} gap={[500, 500]} className={styles.watermark}>
                <Flex vertical className={styles.resultContainer}>
                    <Result
                        icon={<LogoText variant={'dark'} />}
                        title={<Typography.Title level={3}>{t('You Are Logged Out')}</Typography.Title>}
                        subTitle={t('You need to be authenticated to access the data portal')}
                        extra={[
                            <Button
                                key={'sign-in-button'}
                                type={'primary'}
                                onClick={handleSigninRedirect}
                                icon={<ArrowRightOutlined />}
                                loading={isLoading}
                                className={styles.largeButton}
                            >
                                {t('Sign in')}
                            </Button>,
                        ]}
                        className={styles.result}
                    />
                </Flex>
            </Watermark>
        </>
    );
}
