import { Form, Input, Select, Skeleton } from 'antd';
import type { FormInstance } from 'antd/es/form/hooks/useForm';
import TextArea from 'antd/es/input/TextArea';
import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useDebouncedCallback } from 'use-debounce';
import { ResourceNameFormItem } from '@/components/resource-name/resource-name-form-item.tsx';
import { MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useGetDataProductsLifecyclesQuery } from '@/store/api/services/generated/configurationDataProductLifecyclesApi.ts';
import { useGetDataProductsTypesQuery } from '@/store/api/services/generated/configurationDataProductTypesApi.ts';
import { useGetDomainsQuery } from '@/store/api/services/generated/configurationDomainsApi.ts';
import { useGetTagsQuery } from '@/store/api/services/generated/configurationTagsApi.ts';
import type { DataProductCreate, GetDataProductResponse } from '@/store/api/services/generated/dataProductsApi.ts';
import {
    ResourceNameModel,
    useLazySanitizeResourceNameQuery,
    useLazyValidateResourceNameQuery,
    useResourceNameConstraintsQuery,
} from '@/store/api/services/generated/resourceNamesApi.ts';
import { useGetUsersQuery } from '@/store/api/services/generated/usersApi.ts';
import { useGetDataProductOwnerIds } from '@/utils/data-product-user-role.helper.ts';
import { selectFilterOptionByLabel, selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';

type Props<T extends DataProductCreate> = {
    form: FormInstance<T>;
    currentDataProduct?: GetDataProductResponse;
    mode: 'create' | 'edit';
    setAreFormItemsLoading: (loading: boolean) => void;
};
export const DataProductFormItems = <T extends DataProductCreate>({
    form: formT,
    mode,
    currentDataProduct,
    setAreFormItemsLoading,
}: Props<T>) => {
    const form = formT as unknown as FormInstance<DataProductCreate>;
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser);

    const { data: lifecycles = undefined, isFetching: isFetchingLifecycles } = useGetDataProductsLifecyclesQuery();
    const { data: { domains = [] } = {}, isFetching: isFetchingDomains } = useGetDomainsQuery();
    const { data: dataProductTypes = undefined, isFetching: isFetchingDataProductTypes } =
        useGetDataProductsTypesQuery();
    const { data: { users: dataProductOwners = [] } = {}, isFetching: isFetchingUsers } = useGetUsersQuery();
    const { data: { tags: availableTags = [] } = {}, isFetching: isFetchingTags } = useGetTagsQuery();
    const [sanitizeResourceName, { data: sanitizedResourceName, isSuccess: sanitizedResourceNameSuccess }] =
        useLazySanitizeResourceNameQuery();
    const [validateResourceName] = useLazyValidateResourceNameQuery();
    const { data: constraints } = useResourceNameConstraintsQuery();
    useEffect(() => {
        setAreFormItemsLoading(
            (isFetchingTags ||
                isFetchingUsers ||
                isFetchingDataProductTypes ||
                isFetchingDomains ||
                isFetchingLifecycles) ??
                true,
        );
    }, [
        isFetchingTags,
        isFetchingUsers,
        isFetchingDataProductTypes,
        isFetchingDomains,
        isFetchingLifecycles,
        setAreFormItemsLoading,
    ]);

    const dataProductNameValue = Form.useWatch('name', form);

    const [canEditResourceName, setCanEditResourceName] = useState<boolean>(false);

    const dataProductTypeSelectOptions = dataProductTypes?.data_product_types.map((type) => ({
        label: type.name,
        value: type.id,
    }));
    const userSelectOptions = dataProductOwners.map((owner) => ({
        label: `${owner.first_name} ${owner.last_name} (${owner.email})`,
        value: owner.id,
        disabled: owner.id === currentUser?.id,
    }));
    const tagSelectOptions = availableTags.map((tag) => ({ label: tag.value, value: tag.id }));

    const fetchResourceNameDebounced = useDebouncedCallback((name: string) => sanitizeResourceName(name), 500);

    useEffect(() => {
        if (mode === 'create' && !canEditResourceName) {
            form.setFields([
                {
                    name: 'namespace',
                    validating: true,
                    errors: [],
                },
            ]);
            fetchResourceNameDebounced(dataProductNameValue ?? '');
        }
    }, [form, mode, canEditResourceName, dataProductNameValue, fetchResourceNameDebounced]);

    useEffect(() => {
        if (mode === 'create' && !canEditResourceName && sanitizedResourceNameSuccess && sanitizedResourceName) {
            form.setFieldValue('namespace', sanitizedResourceName.resource_name);
            form.validateFields(['namespace']);
        }
    }, [form, mode, canEditResourceName, sanitizedResourceName, sanitizedResourceNameSuccess]);

    const resourceNameValidationCallback = useCallback(
        (resourceName: string) =>
            validateResourceName({ resourceName: resourceName, model: ResourceNameModel.DataProduct }).unwrap(),
        [validateResourceName],
    );

    const ownerIds = useGetDataProductOwnerIds(currentDataProduct?.id);

    if (mode === 'edit' && (!currentDataProduct || ownerIds === undefined)) {
        return <Skeleton active />;
    }

    return (
        <>
            <Form.Item<DataProductCreate>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your Data Product')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide the name of the Data Product'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <ResourceNameFormItem
                form={form}
                tooltip={t('The namespace of the Data Product')}
                max_length={constraints?.max_length}
                editToggleDisabled={mode === 'edit'}
                canEditResourceName={canEditResourceName}
                toggleCanEditResourceName={() => setCanEditResourceName((prev) => !prev)}
                validationRequired={mode === 'create'}
                validateResourceName={resourceNameValidationCallback}
            />
            <Form.Item<DataProductCreate>
                name={'owners'}
                label={t('Owners')}
                tooltip={t('The owners of the Data Product')}
                rules={[
                    {
                        required: true,
                        message: t('Please select at least one owner for the Data Product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingUsers}
                    mode={'multiple'}
                    options={userSelectOptions}
                    showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                    disabled={mode !== 'create'}
                    tokenSeparators={[',']}
                />
            </Form.Item>
            <Form.Item<DataProductCreate>
                name={'type_id'}
                label={t('Type')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the type of the Data Product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingDataProductTypes}
                    allowClear
                    showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                    options={dataProductTypeSelectOptions}
                />
            </Form.Item>
            <Form.Item<DataProductCreate>
                name={'lifecycle_id'}
                label={t('Status')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the status of the Data Product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingLifecycles}
                    options={lifecycles?.data_product_life_cycles.map((lifecycle) => ({
                        value: lifecycle.id,
                        label: lifecycle.name,
                    }))}
                    showSearch={{ filterOption: selectFilterOptionByLabelAndValue }}
                    allowClear
                />
            </Form.Item>
            <Form.Item<DataProductCreate>
                name={'domain_id'}
                label={t('Domain')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the domain of the Data Product'),
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
            <Form.Item<DataProductCreate> name={'tag_ids'} label={t('Tags')}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select Data Product tags')}
                    mode={'multiple'}
                    options={tagSelectOptions}
                    showSearch={{ filterOption: selectFilterOptionByLabel }}
                />
            </Form.Item>
            <Form.Item<DataProductCreate>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the Data Product')}
                rules={[
                    {
                        required: true,
                        message: t('Please provide a description for the Data Product'),
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
