import { Form } from 'antd';
import TextArea from 'antd/es/input/TextArea';
import { t } from 'i18next';

export const JustificationFormItem = () => {
    return (
        <Form.Item
            name="justification"
            label={t('Business justification')}
            rules={[
                {
                    required: true,
                    message: t('Please explain why you need access to these Output Ports'),
                },
            ]}
        >
            <TextArea rows={4} placeholder={t('Explain why you need access to these Output Ports')} />
        </Form.Item>
    );
};
