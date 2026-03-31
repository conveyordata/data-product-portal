import { ArrowRightOutlined, EnvironmentOutlined, FundViewOutlined, SearchOutlined } from '@ant-design/icons';
import { Button, Card, Col, Row, Typography } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { ApplicationPaths } from '@/types/navigation.ts';
import styles from './quick-actions.module.scss';

const { Title, Text, Paragraph } = Typography;

interface ActionCardData {
    icon: ReactNode;
    title: string;
    description: string;
    primaryAction: {
        label: string;
        route: string;
    };
    color: 'blue' | 'green' | 'orange';
}

export function QuickActions() {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const actions: ActionCardData[] = [
        {
            icon: <SearchOutlined />,
            title: t('Discover Data Products'),
            description: t('Find, understand, and access data.'),
            primaryAction: { label: t('Browse Marketplace'), route: ApplicationPaths.Marketplace },
            color: 'blue',
        },
        {
            icon: <FundViewOutlined />,
            title: t('Manage Products'),
            description: t('Monitor and maintain your Data Products.'),
            primaryAction: { label: t('Product Studio'), route: ApplicationPaths.Studio },
            color: 'green',
        },
        {
            icon: <EnvironmentOutlined />,
            title: t('Navigate Data Landscape'),
            description: t('Visualise and harmonise your data landscape.'),
            primaryAction: { label: t('Domain Explorer'), route: ApplicationPaths.Explorer },
            color: 'orange',
        },
    ];

    return (
        <>
            <div style={{ marginBottom: 24 }}>
                <Title level={3} style={{ margin: 0, marginBottom: 4 }}>
                    {t('What would you like to do today?')}
                </Title>
                <Text type="secondary">{t('Select your goal to get started')}</Text>
            </div>

            <Row gutter={[24, 24]}>
                {actions.map((action) => (
                    <Col xs={24} md={12} lg={8} key={action.title}>
                        <Card classNames={{ root: `${styles.card} ${styles[action.color]}`, body: styles.cardBody }}>
                            <div>
                                <div className={`${styles.icon} ${styles[action.color]}`}>{action.icon}</div>

                                <Title level={5} style={{ margin: 0, marginBottom: 4 }}>
                                    {action.title}
                                </Title>

                                <Paragraph className={styles.subText} style={{ marginBottom: 24 }}>
                                    {action.description}
                                </Paragraph>
                            </div>

                            <Button
                                block
                                type="primary"
                                icon={<ArrowRightOutlined />}
                                iconPlacement="end"
                                onClick={() => navigate(action.primaryAction.route)}
                                className={`${styles.button} ${styles[action.color]}`}
                            >
                                {action.primaryAction.label}
                            </Button>
                        </Card>
                    </Col>
                ))}
            </Row>
        </>
    );
}
