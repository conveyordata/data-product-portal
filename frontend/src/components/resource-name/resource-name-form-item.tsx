import { EditOutlined } from '@ant-design/icons';
import { Button, Form, type FormInstance, Input, Space } from 'antd';
import type { Rule } from 'antd/es/form';
import { useTranslation } from 'react-i18next';
import {
    type ResourceNameValidation,
    ResourceNameValidityType,
} from '@/store/api/services/generated/resourceNamesApi.ts';
import styles from './resource-name-form-item.module.scss';

type Props = {
    form: FormInstance;
    tooltip?: string;
    max_length?: number;
    editToggleDisabled?: boolean;
    canEditResourceName?: boolean;
    toggleCanEditResourceName?: () => void;
    validationRequired?: boolean;
    validateResourceName?: (resourceName: string) => Promise<ResourceNameValidation>;
};

const DEBOUNCE = 500;

export function ResourceNameFormItem({
    form,
    tooltip,
    max_length,
    editToggleDisabled = false,
    canEditResourceName = false,
    toggleCanEditResourceName,
    validationRequired = false,
    validateResourceName = async () => {
        return { validity: ResourceNameValidityType.Valid };
    },
}: Props) {
    const { t } = useTranslation();

    const validationRules: Rule[] = [
        {
            required: canEditResourceName,
            message: t('Please input a namespace'),
        },
        {
            validator: async (_, value) => {
                if (!canEditResourceName && !value) {
                    return Promise.resolve();
                }

                const validationResponse = await validateResourceName(value);

                switch (validationResponse.validity) {
                    case ResourceNameValidityType.Valid:
                        return Promise.resolve();
                    case ResourceNameValidityType.InvalidLength:
                        return Promise.reject(new Error(t('Namespace is too long')));
                    case ResourceNameValidityType.InvalidCharacters:
                        return Promise.reject(new Error(t('Namespace contains invalid characters')));
                    case ResourceNameValidityType.Duplicate:
                        return Promise.reject(new Error(t('This namespace is already in use')));
                    default:
                        return Promise.reject(new Error(t('Unknown namespace validation error')));
                }
            },
        },
    ];

    return (
        <Form.Item label={t('Namespace')} tooltip={tooltip} required>
            <Space.Compact orientation="horizontal" className={styles.resourceNameFormField}>
                <Form.Item
                    name={'namespace'}
                    noStyle
                    hasFeedback
                    validateFirst
                    validateDebounce={DEBOUNCE}
                    rules={validationRequired ? validationRules : []}
                >
                    <Input
                        disabled={!canEditResourceName}
                        showCount
                        maxLength={max_length}
                        onChange={(e) => {
                            const lowerCaseValue = e.target.value.toLowerCase();
                            form.setFieldValue('namespace', lowerCaseValue);
                        }}
                    />
                </Form.Item>
                <Button onClick={toggleCanEditResourceName} disabled={editToggleDisabled}>
                    <EditOutlined />
                </Button>
            </Space.Compact>
        </Form.Item>
    );
}
