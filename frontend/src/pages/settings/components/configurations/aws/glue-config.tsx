import { Col, Form, Input, Typography } from 'antd';

export const AWSGlueConfig = ({ config, identifier }) => {
    return (
        <Col>
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
                <Form.Item required name={[config.name, 'identifier']} hidden>
                    <Input />
                </Form.Item>
                <Form.Item
                    rules={[
                        {
                            required: true,
                            message: 'Please enter a Database name',
                        },
                    ]}
                    name={[config.name, 'database']}
                    label="Database name"
                >
                    <Input />
                </Form.Item>
                <Form.Item
                    rules={[
                        {
                            required: true,
                            message: 'Please enter a Bucket identifier',
                        },
                    ]}
                    name={[config.name, 'bucket_identifier']}
                    label="Bucket identifier"
                >
                    <Input />
                </Form.Item>
                <Form.Item
                    rules={[
                        {
                            required: true,
                            message: 'Please enter a S3 path',
                        },
                    ]}
                    name={[config.name, 's3_path']}
                    label="S3 path"
                >
                    <Input />
                </Form.Item>
            </div>
        </Col>
    );
};
