import { BellOutlined, CheckCircleOutlined, MessageOutlined } from '@ant-design/icons';
import { Button, Card, Col, Divider, Flex, Form, Row, Select, Space, Typography } from 'antd';
import TextArea from 'antd/es/input/TextArea';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';
import CartOutputPort from '@/pages/cart/cart-output-port.component.tsx';
import styles from '@/pages/data-product/data-product.module.scss';
import { cartData } from '@/store/test-data.tsx';

export function Cart() {
    const { t } = useTranslation();
    return (
        <Row gutter={16}>
            <Col span={16}>
                {/*<Flex gap="small">*/}
                <Space direction="vertical" size="small">
                    {cartData.map((d) => (
                        <CartOutputPort
                            key={d.outputPortName}
                            outputPortName={d.outputPortName}
                            dataProductName={d.dataProductName}
                            description={d.description}
                            domain={d.domain}
                            dataProductLifecycle={d.dataProductLifecycle}
                        />
                    ))}
                </Space>
            </Col>
            <Col span={8}>
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
                        <Flex gap={'small'} align={'flex-start'}>
                            <CheckCircleOutlined className={clsx(styles.defaultIcon, styles.xSmall)} />
                            <Typography.Text>{t('Owners typically respond within 24-48 hours')}</Typography.Text>
                        </Flex>
                        <Flex gap={'small'} align={'flex-start'}>
                            <BellOutlined className={clsx(styles.defaultIcon, styles.xSmall)} />
                            <Typography.Text>
                                {t('You will get notified when access is granted or denied')}
                            </Typography.Text>
                        </Flex>
                        <Flex gap={'small'} align={'flex-start'}>
                            <MessageOutlined className={clsx(styles.defaultIcon, styles.xSmall)} />
                            <Typography.Text>{t('Message owners directly for questions')}</Typography.Text>
                        </Flex>
                    </Flex>
                </Card>
            </Col>
        </Row>
    );
}
