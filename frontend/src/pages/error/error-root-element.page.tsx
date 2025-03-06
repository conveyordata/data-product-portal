import { Button, Result } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { isRouteErrorResponse, useNavigate, useRouteError } from 'react-router';

import { Logout } from '@/pages/auth/logout/logout-page.tsx';
import { ApplicationPaths } from '@/types/navigation.ts';
import { isDevMode } from '@/utils/env-mode.helper.ts';

export function ErrorRootElement() {
    const error = useRouteError();
    const navigate = useNavigate();
    const { t } = useTranslation();

    useEffect(() => {
        if (isDevMode) {
            console.error(error);
        }
    }, [error]);

    if (isRouteErrorResponse(error)) {
        if (error.status === 404) {
            return (
                <Result
                    status="404"
                    title="404"
                    subTitle={t('Sorry, the page you visited does not exist')}
                    extra={
                        <Button type="primary" onClick={() => navigate(ApplicationPaths.Home)}>
                            {t('Back Home')}
                        </Button>
                    }
                />
            );
        }

        if (error.status === 401) {
            return <Logout />;
        }
    }

    return (
        <Result
            status="500"
            title="500"
            subTitle={t('Sorry, something went wrong')}
            extra={
                <Button type="primary" onClick={() => navigate(ApplicationPaths.Home)}>
                    {t('Back Home')}
                </Button>
            }
        />
    );
}
