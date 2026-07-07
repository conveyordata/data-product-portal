import { Form, Input, Select } from 'antd';
import TextArea from 'antd/es/input/TextArea';
import { useTranslation } from 'react-i18next';
import { MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { useGetDomainsQuery } from '@/store/api/services/generated/configurationDomainsApi.ts';
import type { Exploration } from '@/store/api/services/generated/explorationsApi.ts';
import { selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';

export const ExplorationFormItems = () => {
    const { t } = useTranslation();

    const { data: { domains = [] } = {}, isFetching: isFetchingDomains } = useGetDomainsQuery();

    return (
        <>
            <Form.Item<Exploration>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your Exploration')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide the name of the Exploration'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <Form.Item<Exploration>
                name={'namespace'}
                label={t('Namespace')}
                tooltip={t('The namespace of your Exploration')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide a namespace'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <Form.Item<Exploration>
                name={'domain'}
                label={t('Domain')}
                tooltip={t('The domain to which this Exploration belongs')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the domain of the Exploration'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingDomains}
                    options={domains.map((domain) => ({ label: domain.name, value: domain.id }))}
                    showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                    allowClear
                />
            </Form.Item>
            <Form.Item<Exploration>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for your Exploration')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide a description for the Exploration'),
                    },
                    {
                        max: MAX_DESCRIPTION_INPUT_LENGTH,
                        message: t('Description must be less than {{length}} characters', {
                            length: MAX_DESCRIPTION_INPUT_LENGTH,
                        }),
                    },
                ]}
            >
                <TextArea rows={4} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
            </Form.Item>
        </>
    );
};
