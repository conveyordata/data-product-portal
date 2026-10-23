import { Button, Flex, Select, Table, type TableColumnsType, Tag } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import {
    type EnvironmentConfigurationProperty,
    useGetTechnicalAssetEnvironmentConfigurationQuery,
    useUpdateTechnicalAssetEnvironmentConfigurationMutation,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';

const INHERIT = '';

type Props = {
    technicalAssetId: string;
    dataProductId: string;
};

export function ConfigurationTab({ technicalAssetId, dataProductId }: Props) {
    const { data } = useGetTechnicalAssetEnvironmentConfigurationQuery({ id: technicalAssetId, dataProductId });

    if (!data) {
        return <LoadingSpinner />;
    }

    return (
        <ConfigurationMatrix
            technicalAssetId={technicalAssetId}
            dataProductId={dataProductId}
            properties={data.properties}
        />
    );
}

function ConfigurationMatrix({
    technicalAssetId,
    dataProductId,
    properties,
}: Props & { properties: EnvironmentConfigurationProperty[] }) {
    const { t } = useTranslation();
    const [save, { isLoading: isSaving }] = useUpdateTechnicalAssetEnvironmentConfigurationMutation();
    const [baseValues, setBaseValues] = useState<Record<string, string>>(() =>
        Object.fromEntries(properties.map((property) => [property.name, property.base_value])),
    );
    const [overrides, setOverrides] = useState(() => {
        const result: Record<string, Record<string, string>> = {};
        for (const property of properties) {
            for (const environment of property.environments) {
                if (environment.override !== null) {
                    result[environment.environment_id] = {
                        ...result[environment.environment_id],
                        [property.name]: environment.override,
                    };
                }
            }
        }
        return result;
    });
    const environments = properties[0]?.environments ?? [];

    const setOverride = (environmentId: string, name: string, value: string) =>
        setOverrides((current) => {
            const { [name]: _, ...rest } = current[environmentId] ?? {};
            return { ...current, [environmentId]: value === INHERIT ? rest : { ...rest, [name]: value } };
        });

    async function handleSave() {
        await save({
            dataProductId,
            id: technicalAssetId,
            updateTechnicalAssetEnvironmentConfigurationRequest: { base_values: baseValues, overrides },
        }).unwrap();
        dispatchMessage({ content: t('Configuration saved'), type: 'success' });
    }

    const toOptions = (property: EnvironmentConfigurationProperty) =>
        property.allowed_values.map((value) => ({ label: value, value }));

    const columns: TableColumnsType<EnvironmentConfigurationProperty> = [
        { title: t('Property'), dataIndex: 'label', key: 'label' },
        {
            title: t('Base'),
            key: 'base',
            render: (_, property) => (
                <Select
                    value={baseValues[property.name]}
                    options={toOptions(property)}
                    onChange={(value) => setBaseValues((current) => ({ ...current, [property.name]: value }))}
                />
            ),
        },
        ...environments.map((environment) => ({
            key: environment.environment_id,
            title: environment.name,
            render: (_: unknown, property: EnvironmentConfigurationProperty) => {
                const override = overrides[environment.environment_id]?.[property.name];
                return (
                    <Flex align="center" gap="small">
                        <Select
                            value={override}
                            placeholder={baseValues[property.name]}
                            options={[{ label: t('Inherit'), value: INHERIT }, ...toOptions(property)]}
                            onChange={(value) => setOverride(environment.environment_id, property.name, value)}
                        />
                        {override && <Tag color="blue">{t('Override')}</Tag>}
                    </Flex>
                );
            },
        })),
    ];

    return (
        <Flex vertical gap="middle">
            <Table rowKey="name" columns={columns} dataSource={properties} pagination={false} size="small" />
            <Flex justify="end">
                <Button type="primary" loading={isSaving} onClick={handleSave}>
                    {t('Save')}
                </Button>
            </Flex>
        </Flex>
    );
}
