import { DeleteOutlined } from '@ant-design/icons';
import { Card, Descriptions, Flex, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';

type Props = {
    outputPortName: string;
    dataProductName: string;
    description: string;
    domain: string;
    dataProductLifecycle: DataProductLifeCycleContract;
};
export default function CartOutputPort({
    outputPortName,
    dataProductName,
    description,
    domain,
    dataProductLifecycle,
}: Props) {
    const { t } = useTranslation();
    return (
        <Card>
            <Flex justify="space-between" align="start">
                <Descriptions
                    size={'small'}
                    column={{ xl: 1, xxl: 3 }}
                    colon
                    items={[
                        {
                            key: '0',
                            label: null,
                            children: <Typography.Title level={3}>{outputPortName}</Typography.Title>,
                            span: 'filled',
                        },
                        {
                            key: '1',
                            label: <Typography.Text strong>Data product</Typography.Text>,
                            children: dataProductName,
                        },
                        //TODO refactor common code with DataProductDescription
                        {
                            key: '2',
                            label: <Typography.Text strong>{t('Status')}</Typography.Text>,
                            children: <Tag color={dataProductLifecycle.color}>{dataProductLifecycle.name}</Tag>,
                        },
                        {
                            key: '3',
                            label: <Typography.Text strong>{t('Domain')}</Typography.Text>,
                            children: <Typography.Text>{domain}</Typography.Text>,
                        },
                        {
                            key: '4',
                            label: null,
                            children: <Typography.Text>{description}</Typography.Text>,
                            span: 'filled',
                        },
                    ]}
                />
                <DeleteOutlined style={{ marginLeft: 'auto' }} />
            </Flex>
        </Card>
    );
}
