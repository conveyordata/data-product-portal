import { Col, Row } from 'antd';
import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { DataProductsInbox } from '@/pages/home/components/data-products-inbox/data-products-inbox.tsx';
import { DatasetsInbox } from '@/pages/home/components/datasets-inbox/datasets-inbox.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { PendingRequestsInbox } from './components/pending-requests-inbox/pending-requests-inbox';
import styles from './home.module.scss';

const ROW_GUTTER = 96;
const COL_SPAN = 12;

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
            <PendingRequestsInbox />

            <div className={styles.contentSecondary}>
                <Row gutter={ROW_GUTTER}>
                    <Col span={COL_SPAN}>
                        <DataProductsInbox userId={currentUser.id} />
                    </Col>
                    <Col span={COL_SPAN}>
                        <DatasetsInbox userId={currentUser.id} />
                    </Col>
                </Row>
            </div>
        </div>
    );
}
