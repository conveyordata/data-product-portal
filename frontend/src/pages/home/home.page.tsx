import { ExperimentOutlined } from '@ant-design/icons';
import { Button, Col, Row } from 'antd';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import { DataProductsInbox } from '@/pages/home/components/data-products-inbox/data-products-inbox.tsx';
import { DatasetsInbox } from '@/pages/home/components/datasets-inbox/datasets-inbox.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { PendingRequestsInbox } from './components/pending-requests-inbox/pending-requests-inbox';
import styles from './home.module.scss';

const ROW_GUTTER = 96;
const COL_SPAN = 12;

export function Home() {
    const currentUser = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    if (!currentUser) return null;

    return (
        <div className={styles.container}>
            <PendingRequestsInbox />

            <div className={styles.mcpServerSection}>
                <Button
                    type="primary"
                    size="large"
                    icon={<ExperimentOutlined />}
                    className={styles.mcpServerButton}
                    onClick={() => {
                        posthog.capture(PosthogEvents.HOMEPAGE_MCP_CLICKED);
                        window.open(
                            'https://d33vpinjygaq6n.cloudfront.net/docs/user-guide/experimental-features',
                            '_blank',
                            'noopener,noreferrer',
                        );
                    }}
                >
                    {t('Try out our new MCP Server (Experimental)')}
                </Button>
            </div>

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
