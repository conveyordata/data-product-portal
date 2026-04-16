import { Col, Row } from 'antd';
import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { AlertBanner } from '@/pages/home/components/alert-banner/alert-banner.tsx';
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
            <AlertBanner />

            <Row gutter={[48, 48]}>
                <Col span={24}>
                    <QuickActions />
                </Col>
            </Row>
        </div>
    );
}
