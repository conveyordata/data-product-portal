import { ArrowRightOutlined, BookOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { Card, Flex, Steps, Typography, theme } from 'antd';
import { Trans, useTranslation } from 'react-i18next';

import { useTabParam } from '@/hooks/use-tab-param.tsx';
import { ExplorationTabKeys } from '@/pages/exploration/exploration-tab-keys.ts';

const { Title, Text, Link } = Typography;

export const ExplorationStart = () => {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const { onTabChange } = useTabParam(ExplorationTabKeys.Start, Object.values(ExplorationTabKeys));

    const steps = [
        {
            title: <Text strong>{t('View Your Data Sources')}</Text>,
            description: (
                <Text type="secondary">
                    <Trans t={t}>
                        Check the
                        <Link onClick={() => onTabChange(ExplorationTabKeys.InputPorts)}> Input Ports </Link>
                        tab to see the status of access requests to Output Ports and explore schemas and sample rows of
                        datasets.
                    </Trans>
                </Text>
            ),
        },
        {
            title: <Text strong>{t('Run Queries')}</Text>,
            description: (
                <Text type="secondary">
                    {t('Open your preferred SQL tool and start querying datasets available in the ')}
                    <Link onClick={() => onTabChange(ExplorationTabKeys.InputPorts)}>{t('Input Ports')}</Link>
                    {t(' tab.')}
                </Text>
            ),
        },
    ];

    const guidanceItems = [
        t("This is a private sandbox, your queries aren't visible in the Marketplace."),
        t('Need to share results? You need to create a new Data Product based on your Exploration later.'),
    ];

    return (
        <Flex vertical gap="middle">
            <Card>
                <Flex vertical gap="middle">
                    <Flex align="center" gap="small">
                        <BookOutlined style={{ fontSize: 20, color: token.colorPrimary }} />
                        <Title level={5} style={{ margin: 0 }}>
                            {t('How to use this Exploration')}
                        </Title>
                    </Flex>
                    <Text type="secondary">{t('Follow these steps to get started with exploring data.')}</Text>
                    <Steps orientation="vertical" current={-1} items={steps} />
                </Flex>
            </Card>
            <Card>
                <Flex vertical gap="middle">
                    <Flex align="center" gap="small">
                        <InfoCircleOutlined style={{ fontSize: 20, color: token.colorPrimary }} />
                        <Title level={5} style={{ margin: 0 }}>
                            {t('Further Guidance')}
                        </Title>
                    </Flex>
                    {guidanceItems.map((item) => (
                        <Flex key={item} align="baseline" gap="small">
                            <ArrowRightOutlined style={{ fontSize: 12, color: token.colorTextSecondary }} />
                            <Text type="secondary">{item}</Text>
                        </Flex>
                    ))}
                </Flex>
            </Card>
        </Flex>
    );
};
