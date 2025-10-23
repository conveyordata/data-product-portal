import { DeleteOutlined } from '@ant-design/icons';
import { Button, Card, Descriptions, Flex, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { DatasetsGetContractSingle } from '@/types/dataset/datasets-get.contract.ts';

type Props = {
    dataset: DatasetsGetContractSingle;
};
export default function CartOutputPort({ dataset }: Props) {
    const { t } = useTranslation();
    return (
        <Card>
            <Flex justify="space-between" align="start">
                <Descriptions
                    size={'small'}
                    column={{ xl: 1, xxl: 4 }}
                    colon
                    items={[
                        {
                            key: '0',
                            label: null,
                            children: (
                                <Typography.Title ellipsis={{ tooltip: true }} level={3}>
                                    {dataset.name}
                                </Typography.Title>
                            ),
                            span: 'filled',
                        },
                        {
                            key: '1',
                            label: <Typography.Text strong>Data product</Typography.Text>,
                            children: (
                                <Typography.Text ellipsis={{ tooltip: true }}>
                                    {dataset.data_product_name}
                                </Typography.Text>
                            ),
                            span: 2,
                        },
                        //TODO refactor common code with DataProductDescription
                        {
                            key: '2',
                            label: <Typography.Text strong>{t('Status')}</Typography.Text>,
                            children: <Tag color={dataset.lifecycle.color}>{dataset.lifecycle.name}</Tag>,
                        },
                        {
                            key: '3',
                            label: <Typography.Text strong>{t('Domain')}</Typography.Text>,
                            children: (
                                <Typography.Text ellipsis={{ tooltip: true }}>{dataset.domain.name}</Typography.Text>
                            ),
                        },
                        {
                            key: '4',
                            label: null,
                            children: <Typography.Text>{dataset.description}</Typography.Text>,
                            span: 'filled',
                        },
                    ]}
                />
                <Button type={'text'} icon={<DeleteOutlined />} danger style={{ marginLeft: 'auto' }} />
            </Flex>
        </Card>
    );
}
