import { Form } from 'antd';
import TextArea from 'antd/es/input/TextArea';
import { t } from 'i18next';
import type { ChangeEventHandler, ReactNode } from 'react';

type Props = {
    extra?: ReactNode;
    onChange?: ChangeEventHandler<HTMLTextAreaElement> | undefined;
};

export const JustificationFormItem = ({ extra, onChange }: Props) => {
    return (
        <Form.Item
            name="justification"
            label={t('Business justification')}
            extra={extra}
            rules={[
                {
                    required: true,
                    message: t('Please explain why you need access to these Output Ports'),
                },
            ]}
        >
            <TextArea
                rows={4}
                onChange={onChange}
                placeholder={t('Explain why you need access to these Output Ports')}
            />
        </Form.Item>
    );
};
