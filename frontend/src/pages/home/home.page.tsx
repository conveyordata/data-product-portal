import { Flex } from 'antd';
import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { HomeNotifications } from '@/pages/home/components/home-notifications/home-notifications.tsx';
import { QuickActions } from '@/pages/home/components/quick-actions/quick-actions.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import styles from './home.module.scss';

export function Home() {
    const currentUser = useSelector(selectCurrentUser);
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        //Home is set in the breadcrumb provider itself, but we need to set it to an empty list otherwise we keep the old breadcrumb
        setBreadcrumbs([]);
    }, [setBreadcrumbs]);
    if (!currentUser) return null;

    return (
        <div className={styles.container}>
            <Flex vertical gap={48}>
                <HomeNotifications />
                <QuickActions />
            </Flex>
        </div>
    );
}
