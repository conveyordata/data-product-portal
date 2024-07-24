import { Button, Form, FormProps, Input, Popconfirm, Select, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import styles from './data-output-form.module.scss';
import {
    useCreateDataProductMutation,
    useGetDataProductByIdQuery,
    useRemoveDataProductMutation,
    useUpdateDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { useGetAllUsersQuery } from '@/store/features/users/users-api-slice.ts';
import { DataOutputCreate, DataOutputCreateFormSchema } from '@/types/data-output';
import { TagCreate } from '@/types/tag';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { generateExternalIdFromName } from '@/utils/external-id.helper.ts';
import { useEffect, useMemo, useState } from 'react';
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
import { DataProductContract } from '@/types/data-product';
import { useCreateDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice';
import { AccessDataTile } from '@/components/data-access/data-access-tile/data-access-tile.component';
import { DataPlatform } from '@/types/data-platform';
import { DataPlatforms } from '@/types/data-platform/data-platform';
import { getDataPlatforms } from '@/pages/data-product/components/data-product-actions/data-product-actions.component';
import { DataOutputPlatformTile } from '@/components/data-outputs/data-output-platform-tile/data-output-platform-tile.component';
import { unescape } from 'querystring';
import { CustomDropdownItemProps } from '@/types/shared';

type Props = {
    mode: 'create';
    dataProductId: string;
};

const { TextArea } = Input;

export function DataOutputForm({ mode, dataProductId }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [selectedDataPlatform, setSelectedDataPlatform] = useState<CustomDropdownItemProps | undefined>(undefined);
    const [selectedConfiguration, setSelectedConfiguration] = useState<CustomDropdownItemProps | undefined>(undefined);
    const currentUser = useSelector(selectCurrentUser);
    const { data: currentDataProduct, isFetching: isFetchingInitialValues } = useGetDataProductByIdQuery(
        dataProductId);
    // const { data: businessAreas = [], isFetching: isFetchingBusinessAreas } = useGetAllBusinessAreasQuery();
    // const { data: dataProductTypes = [], isFetching: isFetchingDataProductTypes } = useGetAllDataProductTypesQuery();
    // const { data: dataProductOwners = [], isFetching: isFetchingUsers } = useGetAllUsersQuery();
    const [createDataOutput, { isLoading: isCreating }] = useCreateDataOutputMutation();
//    const [updateDataProduct, { isLoading: isUpdating }] = useUpdateDataProductMutation();
  //  const [archiveDataProduct, { isLoading: isArchiving }] = useRemoveDataProductMutation();
    const [form] = Form.useForm<DataOutputCreateFormSchema>();
    const dataProductNameValue = Form.useWatch('name', form);
    const canFillInForm = mode === 'create';
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);
    const isLoading = isCreating || isCreating || isFetchingInitialValues;

    // const dataProductTypeSelectOptions = dataProductTypes.map((type) => ({ label: type.name, value: type.id }));
    // const businessAreaSelectOptions = businessAreas.map((area) => ({ label: area.name, value: area.id }));
    // const userSelectOptions = dataProductOwners.map((owner) => ({ label: owner.email, value: owner.id }));

    const onSubmit: FormProps<DataOutputCreateFormSchema>['onFinish'] = async (values) => {
        try {
            if (mode === 'create') {
                const request: DataOutputCreate = {
                    name: values.name,
                    external_id: values.external_id,
                    configuration: values.configuration,
                    owner_id: dataProductId,
                };
                const response = await createDataOutput(request).unwrap();
                dispatchMessage({ content: t('Data product created successfully'), type: 'success' });

                navigate(createDataProductIdPath(response.id));
            }// else if (mode === 'edit' && dataProductId) {
            //     if (!canEditForm) {
            //         dispatchMessage({ content: t('You are not allowed to edit this data product'), type: 'error' });
            //         return;
            //     }
            //     const dataProductMembers = currentDataProduct
            //         ? getDataProductMemberMemberships(currentDataProduct)
            //         : [];
            //     const dataProductOwnerIds = owners.map((owner) => owner.user_id);
            //     const filteredMembers = dataProductMembers.filter(
            //         (member) => !dataProductOwnerIds.includes(member.user_id),
            //     );
            //     const memberships = [...owners, ...filteredMembers];

            //     // const request: DataProductUpdateRequest = {
            //     //     name: values.name,
            //     //     external_id: values.external_id,
            //     //     description: values.description,
            //     //     type_id: values.type_id,
            //     //     business_area_id: values.business_area_id,
            //     //     tags: tags,
            //     //     memberships,
            //     // };
            //     const response = await updateDataProduct({
            //         dataProduct: request,
            //         data_product_id: dataProductId,
            //     }).unwrap();
            //     dispatchMessage({ content: t('Data product updated successfully'), type: 'success' });

            //     navigate(createDataProductIdPath(response.id));
            // }

            form.resetFields();
        } catch (e) {
            const errorMessage = ('Failed to create data output');
            dispatchMessage({ content: errorMessage, type: 'error' });
        }
    };

    const onSubmitFailed: FormProps<DataOutputCreateFormSchema>['onFinishFailed'] = () => {
        dispatchMessage({ content: t('Please check for invalid form fields'), type: 'info' });
    };

    const onDataPlatformClick = (dataPlatform: DataPlatform) => {
        const dropdown = dataPlatforms.filter((platform) => (platform.value === dataPlatform)).at(0)
        if (selectedDataPlatform !== undefined && selectedDataPlatform === dropdown) {
            setSelectedDataPlatform(undefined)
        } else {
            setSelectedDataPlatform(dropdown)
        }
    }
    const onConfigurationClick = (dataPlatform: DataPlatform) => {
        console.log(dataPlatform)
        const dropdown = selectedDataPlatform?.children.filter((platform) => (platform.value === dataPlatform)).at(0)
        console.log(dropdown)
        if (selectedConfiguration !== undefined && selectedConfiguration === dropdown) {
            setSelectedConfiguration(undefined)
        } else {
            setSelectedConfiguration(dropdown)
        }
    }

    const onCancel = () => {
        form.resetFields();
    }
    useEffect(() => {
        if (mode === 'create') {
            form.setFieldsValue({ external_id: generateExternalIdFromName(dataProductNameValue ?? ''), owner: currentDataProduct?.name });
        }
    }, [dataProductNameValue]);

    // useEffect(() => {
    //     if (currentDataProduct && mode === 'edit') {
    //         form.setFieldsValue({
    //             external_id: currentDataProduct.external_id,
    //             name: currentDataProduct.name,
    //             description: currentDataProduct.description,
    //             type_id: currentDataProduct.type.id,
    //             business_area_id: currentDataProduct.business_area.id,
    //             tags: currentDataProduct.tags.map((tag) => tag.value),
    //             owners: getDataProductOwnerIds(currentDataProduct),
    //         });
    //     }
    // }, [currentDataProduct, mode]);

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
            <Form.Item<DataOutputCreateFormSchema>
                name={'name'}
                label={t('Name')}
                tooltip={t('The name of your data output')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the data output'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            {/*Disabled field that will render an external ID everytime the name changes*/}
            <Form.Item<DataOutputCreateFormSchema>
                required
                name={'external_id'}
                label={t('External ID')}
                tooltip={t('The external ID of the data product')}
            >
                <Input disabled />
            </Form.Item>
            <Form.Item<DataOutputCreateFormSchema>
                required
                name={'owner'}
                label={t('Owner')}
                tooltip={t('The data product that owns the data output')}
            >
                <Input disabled />
            </Form.Item>
            <Form.Item>
                <Space wrap className={styles.radioButtonContainer}>
                        {dataPlatforms.filter((dataPlatform) => (dataPlatform.hasConfig)).map((dataPlatform) => (
                            <DataOutputPlatformTile<DataPlatform>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                environments={[]}
                                isDisabled={isLoading}
                                isLoading={isLoading}
                                isSelected={selectedDataPlatform !== undefined && dataPlatform === selectedDataPlatform }
                                //onMenuItemClick={onDataPlatformClick}
                                onTileClick={onDataPlatformClick}
                            />
                        ))}
                    </Space>
            </Form.Item>
            <Form.Item>
                <Space wrap className={styles.radioButtonContainer}>
                    {/* TODO Fetch correct data platform children */}
                        {selectedDataPlatform?.children.map((dataPlatform) => (
                            <DataOutputPlatformTile<DataPlatform>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                environments={[]}
                                isDisabled={isLoading}
                                isSelected={selectedConfiguration !== undefined && dataPlatform === selectedConfiguration}
                                isLoading={isLoading}
                                //isDisabled={isDisabled || isLoading || isLoadingEnvironments || !canAccessData}
                                //isLoading={isLoading || isLoadingEnvironments}
                                //onMenuItemClick={onDataPlatformClick}
                                onTileClick={onConfigurationClick}
                            />
                        ))}
                    </Space>
            </Form.Item>
            <Form.Item
                // TODO Somehow fill this with the S3 object type
                required
                name={ selectedConfiguration?.label }
                label={ selectedConfiguration?.label }
            >
            </Form.Item>
            <Form.Item>
                <Space>
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        loading={isCreating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {t('Create')}
                    </Button>
                    <Button
                        className={styles.formButton}
                        type="default"
                        onClick={onCancel}
                        loading={isCreating}
                        disabled={isLoading || !canFillInForm}
                    >
                        {t('Cancel')}
                    </Button>
                </Space>
            </Form.Item>
        </Form>
    );
}
