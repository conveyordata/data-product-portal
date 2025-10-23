import { BellOutlined, CheckCircleOutlined, MessageOutlined } from '@ant-design/icons';
import { Button, Card, Col, Divider, Flex, Form, Row, Select, Space, Typography, theme } from 'antd';
import TextArea from 'antd/es/input/TextArea';
import { useTranslation } from 'react-i18next';
import CartOutputPort from '@/pages/cart/cart-output-port.component.tsx';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';

export function Cart() {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const { data: datasets, isFetching } = useGetAllDatasetsQuery();
    return (
        <Row gutter={16}>
            <Col span={14}>
                {/*<Flex gap="small">*/}
                <Space direction="vertical" size="small">
                    {!isFetching && datasets?.map((d) => <CartOutputPort key={d.id} dataset={d} />)}
                </Space>
            </Col>
            <Col span={10}>
                <Card title={<Typography.Title level={3}>{t('Request summary')}</Typography.Title>}>
                    <Form layout={'vertical'}>
                        <Form.Item name="data-product" label={'Data product'}>
                            <Select showSearch placeholder="Select a data product">
                                <Select.Option value="1">1</Select.Option>
                            </Select>
                        </Form.Item>
                        <Form.Item name="justification" label={'Justification'}>
                            <TextArea rows={4} placeholder="Explain why you need access to these output ports" />
                        </Form.Item>
                        <Form.Item label={null} style={{ marginBottom: 16 }}>
                            <Button type="primary" htmlType="submit" style={{ width: '100%' }}>
                                Submit access requests
                            </Button>
                        </Form.Item>
                        <Form.Item label={null}>
                            <Button type="default" style={{ width: '100%' }}>
                                Continue browsing
                            </Button>
                        </Form.Item>
                    </Form>
                    <Divider />
                    <Flex vertical>
                        <Typography.Text>
                            <CheckCircleOutlined style={{ color: `${token.colorPrimary}` }} />{' '}
                            {t('Owners typically respond within 24-48 hours')}
                        </Typography.Text>
                        <Typography.Text>
                            <BellOutlined style={{ color: `${token.colorPrimary}` }} />{' '}
                            {t('You will get notified when access is granted or denied')}
                        </Typography.Text>
                        <Typography.Text>
                            <MessageOutlined style={{ color: `${token.colorPrimary}` }} />{' '}
                            {t('Message owners directly for questions')}
                        </Typography.Text>
                    </Flex>
                </Card>
            </Col>
        </Row>
    );
}
