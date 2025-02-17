import { Col, Flex, Form, Row, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './home.module.scss';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { Searchbar } from '@/components/form';
import { DataProductsInbox } from '@/pages/home/components/data-products-inbox/data-products-inbox.tsx';
import { DatasetsInbox } from '@/pages/home/components/datasets-inbox/datasets-inbox.tsx';
import { AgenticSystem } from '@/components/agentic-system/agentic-system.component';

const ROW_GUTTER = 96;
const COL_SPAN = 12;

export function Home() {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser);
    const [searchForm] = Form.useForm();

    if (!currentUser) return null;

    return (
        <div className={styles.container}>
            <Flex className={styles.backgroundImage}>
                <Typography.Title level={2}>
                    {t('Welcome back, {{name}}', { name: currentUser?.first_name })}
                </Typography.Title>
                <div className={styles.searchBar}>
                    <Searchbar form={searchForm} placeholder={t('Search for data products and datasets by name')} />
                </div>
            </Flex>
            <Flex>
                <AgenticSystem />
            </Flex>
            <div className={styles.content}>
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
