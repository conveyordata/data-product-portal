import { Col, Row } from 'antd';
import { useSelector } from 'react-redux';

import { DataProductsInbox } from '@/pages/home/components/data-products-inbox/data-products-inbox.tsx';
import { DatasetsInbox } from '@/pages/home/components/datasets-inbox/datasets-inbox.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';

import { PendingRequestsInbox } from './components/pending-requests-inbox/pending-requests-inbox';
import styles from './home.module.scss';

const ROW_GUTTER = 96;
const COL_SPAN = 12;

export function Home() {
    const currentUser = useSelector(selectCurrentUser);

    if (!currentUser) return null;

    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <Row gutter={ROW_GUTTER}>
                    <Col span={COL_SPAN * 2}>
                        <PendingRequestsInbox />
                    </Col>
                </Row>
            </div>

            <div className={styles.contentSecundary}>
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
