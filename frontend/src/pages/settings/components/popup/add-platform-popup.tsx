import { FormModal } from '@/components/modal/form-modal/form-modal.component.tsx';
import { useTranslation } from 'react-i18next';
import { FormInstance, Form, Select, Button } from 'antd';
import { useGetAllPlatformsQuery } from '@/store/features/platforms/platforms-api-slice';
import { useGetAllPlatformServicesQuery } from '@/store/features/platform-services/platform-services-api-slice';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    settingsForm: FormInstance;
};

export function AddPlatformPopup({ onClose, isOpen, settingsForm }: Props) {
    const { t } = useTranslation();
    const [form] = Form.useForm();

    const settingsPlatforms = settingsForm.getFieldValue('platforms');

    const platformFormValue = Form.useWatch('platform', form);

    const { data: platforms = [], isFetching: isFetchingPlatforms } = useGetAllPlatformsQuery();

    const { data: services = [], isFetching: isFetchingServices } = useGetAllPlatformServicesQuery(
        platformFormValue?.value,
        {
            skip: !platformFormValue,
        },
    );

    // const filteredPlatforms = platforms.filter(
    //     (platform) => !settingsPlatforms.some((existing) => existing.id === platform.id),
    // );
    // const platformsOptions = filteredPlatforms.map((platform) => ({ label: platform.name, value: platform.id }));

    const platformsOptions = platforms.map((platform) => ({ label: platform.name, value: platform.id }));
    const servicesOptions = services.map((service) => ({ label: service.name, value: service.id }));

    // -- PLATFORM AND ONE SERVICE
    const handleSubmit = (formValues) => {
        const settingsPlatforms = settingsForm.getFieldValue('platforms');
        const filteredPlatforms = settingsPlatforms.filter((platform) => platform.id !== formValues.platform.value);
        const settingsServices =
            settingsPlatforms.find((platform) => platform.id === formValues.platform.value)?.services || [];

        if (settingsServices.find((service) => service.id === formValues.service.value)) {
            onClose();
            return;
        }

        const filteredServices = settingsServices.filter((service) => service.id !== formValues.service.value);

        const newPlatform = {
            name: formValues.platform.label,
            id: formValues.platform.value,
            services: [
                ...filteredServices,
                {
                    name: formValues.service.label,
                    id: formValues.service.value,
                    identifiers: [],
                },
            ],
        };

        const newPlatforms = [...filteredPlatforms, newPlatform];

        settingsForm.setFieldValue('platforms', newPlatforms);
        onClose();
    };

    // --- MULTIPLE SERVICES
    // const handleSubmit = (formValues) => {
    //     // console.log(JSON.stringify(values, null, 2));

    //     const settingsPlatforms = settingsForm.getFieldValue('platforms');
    //     const filteredPlatforms = settingsPlatforms.filter((platform) => platform.id !== formValues.platform.value);

    //     const newPlatform = {
    //         name: formValues.platform.label,
    //         id: formValues.platform.value,
    //         services: formValues.service.map((ser) => ({
    //             name: ser.label,
    //             id: ser.value,
    //             identifiers: [],
    //         })),
    //     };

    //     const newPlatforms = [...filteredPlatforms, newPlatform];

    //     settingsForm.setFieldValue('platforms', newPlatforms);
    //     onClose();
    // };

    // ------ ONLY PLATFORM
    // const handleSubmit = (formValues) => {
    //     const settingsPlatforms = settingsForm.getFieldValue('platforms');

    //     const filteredPlatforms = settingsPlatforms.filter((platform) => platform.id !== formValues.platform.value);

    //     const newPlatform = {
    //         name: formValues.platform.label,
    //         id: formValues.platform.value,
    //         services: services.map((service) => ({
    //             name: service.name,
    //             id: service.id,
    //             identifiers: [],
    //         })),
    //     };

    //     const newPlatforms = [...filteredPlatforms, newPlatform];

    //     settingsForm.setFieldValue('platforms', newPlatforms);
    //     onClose();
    // };

    return (
        <FormModal
            title={t('Add Platform/Service')}
            onClose={onClose}
            isOpen={isOpen}
            footer={(_, { CancelBtn }) => <CancelBtn />}
        >
            <Form layout="vertical" form={form} onFinish={handleSubmit}>
                <Form.Item
                    name={'platform'}
                    label={t('Platform')}
                    rules={[
                        {
                            required: true,
                            message: t('Please select a platform'),
                        },
                    ]}
                >
                    <Select
                        labelInValue
                        loading={isFetchingPlatforms}
                        options={platformsOptions}
                        allowClear
                        showSearch
                        // onSelect={() => form.resetFields(['service'])}
                    />
                </Form.Item>
                <Form.Item
                    name={'service'}
                    label={t('Service')}
                    rules={[
                        {
                            required: true,
                            message: t('Please select a service'),
                        },
                    ]}
                >
                    <Select
                        // mode="tags"
                        labelInValue
                        options={servicesOptions}
                        allowClear
                        showSearch
                        disabled={!platformFormValue || isFetchingServices}
                    />
                </Form.Item>
                <Button
                    // className={styles.formButton}
                    type="primary"
                    htmlType={'submit'}
                    disabled={isFetchingPlatforms || !platformFormValue || isFetchingServices}
                >
                    {t('Add')}
                </Button>
            </Form>
        </FormModal>
    );
}
