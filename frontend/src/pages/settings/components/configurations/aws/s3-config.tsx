import { Col, Form, Input, Typography, Switch } from 'antd';

export const AWSS3Config = ({ config, identifier }) => {
    return (
        <Col key={config.name}>
            <div
                style={{
                    padding: 16,
                    borderRadius: 8,
                    border: '1px solid lightgray',
                }}
            >
                <div style={{ textAlign: 'center' }}>
                    <Typography.Title level={4}>{identifier}</Typography.Title>
                </div>

                <Form.Item name={[config.name, 'identifier']} hidden>
                    <Input />
                </Form.Item>
                <Form.Item
                    rules={[
                        {
                            required: true,
                            message: 'Please enter a bucket name',
                        },
                    ]}
                    name={[config.name, 'bucket_name']}
                    label="Bucket name"
                >
                    <Input />
                </Form.Item>
                <Form.Item
                    rules={[
                        {
                            required: true,
                            message: 'Please enter an ARN',
                        },
                    ]}
                    name={[config.name, 'arn']}
                    label="ARN"
                >
                    <Input />
                </Form.Item>
                <Form.Item
                    rules={[
                        {
                            required: true,
                            message: 'Please enter a KMS key',
                        },
                    ]}
                    name={[config.name, 'kms_key']}
                    label="KMS Key"
                >
                    <Input />
                </Form.Item>
                <Form.Item name={[config.name, 'is_default']} valuePropName="checked" label={'Default bucket'}>
                    <Switch checkedChildren="Yes" unCheckedChildren="No" />
                </Form.Item>
            </div>
        </Col>
    );
};
