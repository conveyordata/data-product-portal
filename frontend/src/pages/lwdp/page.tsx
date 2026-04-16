import Icon, {
    ConsoleSqlOutlined,
    GiftOutlined,
    HistoryOutlined,
    ProductOutlined,
    TeamOutlined,
} from '@ant-design/icons';
import { Button, Flex, Space, Table, Tabs, Tag, Tooltip, Typography } from 'antd';
import clsx from 'clsx';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { useSearchOutputPortsQuery } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import styles from './page.module.scss';

const lightweightDataProduct = {
    name: 'My exploration',
    description:
        'This is my personal exploration project, which I can use to gain access to certain output ports to answer business questions',
    domain: {
        name: 'Consulting',
    },
};

export function LightweightDataProduct() {
    const { t } = useTranslation();

    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <ProductOutlined />
                        {t('Product Studio')}
                    </>
                ),
                path: ApplicationPaths.Studio,
            },
            { title: <>{lightweightDataProduct?.name}</> },
        ]);
    }, [setBreadcrumbs, t]);

    const { data: { output_ports: outputPorts = [] } = {}, isFetching } = useSearchOutputPortsQuery({});

    return (
        <Flex vertical className={styles.container}>
            <Space size={'small'}>
                <GiftOutlined className={clsx([styles.defaultIcon, styles.iconBorder])} />
                <Typography.Title level={3} ellipsis={{ tooltip: lightweightDataProduct?.name, rows: 2 }}>
                    {lightweightDataProduct?.name}
                </Typography.Title>
            </Space>
            <Flex vertical gap={'middle'}>
                <Space size={'large'}>
                    <Flex gap={'small'}>
                        <Typography.Text strong>{t('Status')}</Typography.Text>
                        <Tag color={'green'}>Approved</Tag>
                    </Flex>
                    <Flex gap={'small'}>
                        <Typography.Text strong>{t('Domain')}</Typography.Text>
                        <Typography.Text>{lightweightDataProduct.domain.name}</Typography.Text>
                    </Flex>
                </Space>
                <Typography.Paragraph italic>{lightweightDataProduct.description}</Typography.Paragraph>
            </Flex>
            <Tabs
                items={[
                    {
                        key: 'op',
                        icon: <Icon component={dataOutputOutlineIcon} />,
                        label: <Typography.Text>{t('Output Ports')}</Typography.Text>,
                        children: (
                            <Table
                                showHeader={false}
                                loading={isFetching}
                                dataSource={outputPorts}
                                size="small"
                                columns={[
                                    {
                                        title: 'Name',
                                        dataIndex: 'name',
                                    },
                                    {
                                        title: 'Name',
                                        dataIndex: 'description',
                                    },
                                    {
                                        render: () => {
                                            return (
                                                <Tooltip title={'Query this data'}>
                                                    <Button icon={<ConsoleSqlOutlined />} type="default" />
                                                </Tooltip>
                                            );
                                        },
                                    },
                                ]}
                            />
                        ),
                    },
                    {
                        key: 'team',
                        label: <Typography.Text>{t('Team')}</Typography.Text>,
                        icon: <TeamOutlined />,
                        children: <>We are united</>,
                    },
                    {
                        key: 'history',
                        label: t('History'),
                        icon: <HistoryOutlined />,
                        children: <>I am an old product</>,
                    },
                ]}
            />
        </Flex>
    );
}
