import { Button, Form, FormProps, Input, Popconfirm, Select, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './data-product-form.module.scss';
import {
    useCreateDataProductMutation,
    useGetDataProductByIdQuery,
    useRemoveDataProductMutation,
    useUpdateDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetAllUsersQuery } from '@/store/features/users/users-api-slice.ts';
import { DataProductCreate, DataProductCreateFormSchema, DataProductUpdateRequest } from '@/types/data-product';
import { TagCreate } from '@/types/tag';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { generateExternalIdFromName } from '@/utils/external-id.helper.ts';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import { useGetAllBusinessAreasQuery } from '@/store/features/business-areas/business-areas-api-slice.ts';
import {
    getDataProductMemberMemberships,
    getDataProductOwnerIds,
    getIsDataProductOwner,
} from '@/utils/data-product-user-role.helper.ts';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useSelector } from 'react-redux';
import { FORM_GRID_WRAPPER_COLS, MAX_DESCRIPTION_INPUT_LENGTH } from '@/constants/form.constants.ts';
import { selectFilterOptionByLabelAndValue } from '@/utils/form.helper.ts';
import { useGetAllDataProductTypesQuery } from '@/store/features/data-product-types/data-product-types-api-slice.ts';
import { DataProductMembershipRole, DataProductUserMembershipCreateContract } from '@/types/data-product-membership';

type Props = {
    mode: 'create' | 'edit';
    dataProductId?: string;
};

const { TextArea } = Input;

export function DataProductForm({ mode, dataProductId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(
        dataProductId || '',
        {
            skip: mode === 'create' || !dataProductId,
        },
    );
    const { data: businessAreas = [], isFetching: isFetchingBusinessAreas } = useGetAllBusinessAreasQuery();
    const { data: dataProductTypes = [], isFetching: isFetchingDataProductTypes } = useGetAllDataProductTypesQuery();
    const { data: dataProductOwners = [], isFetching: isFetchingUsers } = useGetAllUsersQuery();
    const [createDataProduct, { isLoading: isCreating }] = useCreateDataProductMutation();
    const [updateDataProduct, { isLoading: isUpdating }] = useUpdateDataProductMutation();
    const [archiveDataProduct, { isLoading: isArchiving }] = useRemoveDataProductMutation();
    const [form] = Form.useForm<DataProductCreateFormSchema>();
    const dataProductNameValue = Form.useWatch('name', form);

    const canEditForm = Boolean(
        mode === 'edit' &&
            currentDataProduct &&
            currentUser?.id &&
            (getIsDataProductOwner(currentDataProduct, currentUser?.id) || currentUser?.is_admin),
    );
    const canFillInForm = mode === 'create' || canEditForm;

    const isLoading = isCreating || isUpdating || isCreating || isUpdating || isFetchingInitialValues;

    const dataProductTypeSelectOptions = dataProductTypes.map((type) => ({ label: type.name, value: type.id }));
    const businessAreaSelectOptions = businessAreas.map((area) => ({ label: area.name, value: area.id }));
    const userSelectOptions = dataProductOwners.map((owner) => ({ label: owner.email, value: owner.id }));

    const onSubmit: FormProps<DataProductCreateFormSchema>['onFinish'] = async (values) => {
        try {
            // Right now we are only creating tags and not reusing yet existing ones
            const tags: TagCreate[] = values.tags?.map((tag: string) => ({ value: tag })) ?? [];
            const owners: DataProductUserMembershipCreateContract[] = values.owners.map((owner_id) => ({
                user_id: owner_id,
                role: DataProductMembershipRole.Owner,
            }));

            if (mode === 'create') {
                const request: DataProductCreate = {
                    name: values.name,
                    external_id: values.external_id,
                    description: values.description,
                    memberships: owners,
                    type_id: values.type_id,
                    tags: tags,
                    business_area_id: values.business_area_id,
                };
                const response = await createDataProduct(request).unwrap();
                dispatchMessage({ content: t('Data product created successfully'), type: 'success' });

                navigate(createDataProductIdPath(response.id));
            } else if (mode === 'edit' && dataProductId) {
                if (!canEditForm) {
                    dispatchMessage({ content: t('You are not allowed to edit this data product'), type: 'error' });
                    return;
                }
                const dataProductMembers = currentDataProduct
                    ? getDataProductMemberMemberships(currentDataProduct)
                    : [];
                const dataProductOwnerIds = owners.map((owner) => owner.user_id);
                const filteredMembers = dataProductMembers.filter(
                    (member) => !dataProductOwnerIds.includes(member.user_id),
                );
                const memberships = [...owners, ...filteredMembers];

                const request: DataProductUpdateRequest = {
                    name: values.name,
                    external_id: values.external_id,
                    description: values.description,
                    type_id: values.type_id,
                    business_area_id: values.business_area_id,
                    tags: tags,
                    memberships,
                };
                const response = await updateDataProduct({
                    dataProduct: request,
                    data_product_id: dataProductId,
                }).unwrap();
                dispatchMessage({ content: t('Data product updated successfully'), type: 'success' });

                navigate(createDataProductIdPath(response.id));
            }

            form.resetFields();
        } catch (_e) {
            const errorMessage =
                mode === 'edit' ? t('Failed to update data product') : t('Failed to create data product');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onCancel = () => {
        form.resetFields();
        if (mode === 'edit' && dataProductId) {
            navigate(createDataProductIdPath(dataProductId));
        } else {
            navigate(ApplicationPaths.DataProducts);
        }
    };

    const onSubmitFailed: FormProps<DataProductCreateFormSchema>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const handleArchiveDataProduct = async () => {
        if (canEditForm && currentDataProduct) {
            try {
                await archiveDataProduct(currentDataProduct?.id).unwrap();
                dispatchMessage({ content: t('Data product archived successfully'), type: 'success' });
                navigate(ApplicationPaths.DataProducts);
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to archive data product, please try again later'),
                    type: 'error',
                });
            }
        }
    };

    useEffect(() => {
        if (mode === 'create') {
            form.setFieldsValue({ external_id: generateExternalIdFromName(dataProductNameValue ?? '') });
        }
    }, [dataProductNameValue]);

    useEffect(() => {
        if (currentDataProduct && mode === 'edit') {
            form.setFieldsValue({
                external_id: currentDataProduct.external_id,
                name: currentDataProduct.name,
                description: currentDataProduct.description,
                type_id: currentDataProduct.type.id,
                business_area_id: currentDataProduct.business_area.id,
                tags: currentDataProduct.tags.map((tag) => tag.value),
                owners: getDataProductOwnerIds(currentDataProduct),
            });
        }
    }, [currentDataProduct, mode]);

    return (
        <Form
            form={form}
            labelCol={FORM_GRID_WRAPPER_COLS}
            wrapperCol={FORM_GRID_WRAPPER_COLS}
            layout="vertical"
            onFinish={onSubmit}
            onFinishFailed={onSubmitFailed}
            autoComplete={'off'}
            requiredMark={'optional'}
            labelWrap
            disabled={isLoading || !canFillInForm}
        >
            <Form.Item<DataProductCreateFormSchema>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your data product')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the data product'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            {/*Disabled field that will render an external ID everytime the name changes*/}
            <Form.Item<DataProductCreateFormSchema>
                required
                name={'external_id'}
                label={t('External ID')}
                tooltip={t('The external ID of the data product')}
            >
                <Input disabled />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'owners'}
                label={t('Owners')}
                tooltip={t('The owners of the data product')}
                rules={[
                    {
                        required: true,
                        message: t('Please select at least one owner for the data product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingUsers}
                    mode={'multiple'}
                    options={userSelectOptions}
                    filterOption={selectFilterOptionByLabelAndValue}
                    allowClear
                    tokenSeparators={[',']}
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'type_id'}
                label={t('Type')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the type of the data product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingDataProductTypes}
                    allowClear
                    showSearch
                    options={dataProductTypeSelectOptions}
                    filterOption={selectFilterOptionByLabelAndValue}
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'business_area_id'}
                label={t('Business Area')}
                rules={[
                    {
                        required: true,
                        message: t('Please select the business area of the data product'),
                    },
                ]}
            >
                <Select
                    loading={isFetchingBusinessAreas}
                    options={businessAreaSelectOptions}
                    filterOption={selectFilterOptionByLabelAndValue}
                    allowClear
                    showSearch
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema> name={'tags'} label={t('Tags')}>
                <Select
                    tokenSeparators={[',']}
                    placeholder={t('Select data product tags')}
                    mode={'tags'}
                    options={[]}
                />
            </Form.Item>
            <Form.Item<DataProductCreateFormSchema>
                name={'description'}
                label={t('Description')}
                tooltip={t('A description for the data product')}
                rules={[
                    {
                        required: true,
                        message: t('Please input a description of the data product'),
                    },
                    {
                        max: MAX_DESCRIPTION_INPUT_LENGTH,
                        message: t('Description must be less than 255 characters'),
                    },
                ]}
            >
                <TextArea rows={4} count={{ show: true, max: MAX_DESCRIPTION_INPUT_LENGTH }} />
            </Form.Item>
            <Form.Item>
                <Space>
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isCreating || isUpdating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {mode === 'edit' ? t('Edit') : t('Create')}
                    </Button>
                    <Button
                        className={styles.formButton}
                        type="default"
                        onClick={onCancel}
                        loading={isCreating || isUpdating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {t('Cancel')}
                    </Button>
                    {canEditForm && (
                        <Popconfirm
                            title={t('Are you sure you want to archive this data product?')}
                            onConfirm={handleArchiveDataProduct}
                            okText={t('Yes')}
                            cancelText={t('No')}
                        >
                            <Button
                                className={styles.formButton}
                                type="default"
                                danger
                                loading={isArchiving}
                                disabled={isLoading}
                            >
                                {t('Archive')}
                            </Button>
                        </Popconfirm>
                    )}
                </Space>
            </Form.Item>
        </Form>
    );
}
