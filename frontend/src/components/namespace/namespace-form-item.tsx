import { EditOutlined } from '@ant-design/icons';
import { Button, Form, Input, Space } from 'antd';
import { FormInstance } from 'antd/lib';
import { useTranslation } from 'react-i18next';

import { NamespaceValidationResponse, ValidationType } from '@/types/namespace/namespace';

import styles from './namespace-form-item.module.scss';

type Props = {
    form: FormInstance;
    tooltip?: string;
    max_length?: number;
    editToggleDisabled?: boolean;
    canEditNamespace?: boolean;
    toggleCanEditNamespace?: () => void;
    validationRequired?: boolean;
    validateNamespace?: (namespace: string) => Promise<NamespaceValidationResponse>;
};

const DEBOUNCE = 500;

export function NamespaceFormItem({
    form,
    tooltip,
    max_length,
    editToggleDisabled = false,
    canEditNamespace = false,
    toggleCanEditNamespace,
    validationRequired = false,
    validateNamespace = async () => {
        return { validity: ValidationType.VALID };
    },
}: Props) {
    const { t } = useTranslation();

    return (
        <Form.Item label={t('Namespace')} tooltip={tooltip} required>
            <Space.Compact direction="horizontal" className={styles.namespaceFormField}>
                <Form.Item
                    name={'namespace'}
                    noStyle
                    hasFeedback
                    validateFirst
                    validateDebounce={DEBOUNCE}
                    rules={
                        validationRequired
                            ? [
                                  {
                                      required: canEditNamespace,
                                      message: t('Please input a namespace'),
                                  },
                                  {
                                      validator: async (_, value) => {
                                          if (!canEditNamespace && !value) {
                                              return Promise.resolve();
                                          }

                                          const validationResponse = await validateNamespace(value);

                                          switch (validationResponse.validity) {
                                              case ValidationType.VALID:
                                                  return Promise.resolve();
                                              case ValidationType.INVALID_LENGTH:
                                                  return Promise.reject(new Error(t('Namespace is too long')));
                                              case ValidationType.INVALID_CHARACTERS:
                                                  return Promise.reject(
                                                      new Error(t('Namespace contains invalid characters')),
                                                  );
                                              case ValidationType.DUPLICATE_NAMESPACE:
                                                  return Promise.reject(
                                                      new Error(t('This namespace is already in use')),
                                                  );
                                              default:
                                                  return Promise.reject(
                                                      new Error(t('Unknown namespace validation error')),
                                                  );
                                          }
                                      },
                                  },
                              ]
                            : []
                    }
                >
                    <Input
                        disabled={!canEditNamespace}
                        showCount
                        maxLength={max_length}
                        onChange={(e) => {
                            const lowerCaseValue = e.target.value.toLowerCase();
                            form.setFieldValue('namespace', lowerCaseValue);
                        }}
                    />
                </Form.Item>
                <Button onClick={toggleCanEditNamespace} disabled={editToggleDisabled}>
                    <EditOutlined />
                </Button>
            </Space.Compact>
        </Form.Item>
    );
}
