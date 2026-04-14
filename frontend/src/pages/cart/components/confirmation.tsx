import { EditOutlined } from '@ant-design/icons';
import { Button, Collapse, Flex, Form, Input, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

const { Title } = Typography;
export const ConfirmationStep = () => {
    const { t } = useTranslation();
    return (
        <Flex vertical gap={'middle'}>
            <Title level={2}>{t('Please confirm your choices')}</Title>
            <Collapse
                items={[
                    {
                        label: t('You have selected 2 output ports'),
                        children: 'TODO',
                        extra: <Button icon={<EditOutlined />} />,
                    },
                ]}
            />

            <Collapse
                items={[
                    {
                        label: t('You have selected an existing data product: {{dataProduct}}', {
                            dataProduct: 'blabla',
                        }),
                        extra: <Button icon={<EditOutlined />} />,
                    },
                ]}
            />
            <Form layout="vertical" onFinish={() => {}}>
                <Form.Item
                    name="justification"
                    label={'Business justification'}
                    rules={[
                        {
                            required: true,
                            message: t('Please explain why you need access to these Output Ports'),
                        },
                    ]}
                >
                    <Input.TextArea rows={4} placeholder={t('Explain why you need access to these Output Ports')} />
                </Form.Item>
                <Flex justify="flex-end">
                    <Form.Item label={null}>
                        <Button type="primary" htmlType="submit">
                            Submit
                        </Button>
                    </Form.Item>
                </Flex>
            </Form>
        </Flex>
    );
};
