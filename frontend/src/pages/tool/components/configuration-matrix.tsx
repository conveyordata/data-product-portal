import { Button, Empty, Flex, Select, Table, type TableColumnsType, Tag, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    type OverridablePropertyConfiguration,
    type ToolEnvironmentConfiguration,
    useGetToolEnvironmentConfigurationQuery,
    useUpdateToolEnvironmentConfigurationMutation,
} from '@/store/api/services/generated/dataProductsToolsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';

type Props = {
    dataProductId: string;
    toolId: string;
    canEdit: boolean;
};

type Draft = {
    base_values: Record<string, string>;
    overrides: Record<string, Record<string, string>>;
};

const INHERIT = '__inherit__';

function toDraft(configuration: ToolEnvironmentConfiguration): Draft {
    const draft: Draft = { base_values: {}, overrides: {} };
    for (const property of configuration.properties) {
        draft.base_values[property.name] = property.base_value;
        for (const environment of property.environments) {
            if (environment.override !== null) {
                draft.overrides[environment.id] = {
                    ...draft.overrides[environment.id],
                    [property.name]: environment.override,
                };
            }
        }
    }
    return draft;
}

export function ConfigurationMatrix({ dataProductId, toolId, canEdit }: Props) {
    const { t } = useTranslation();
    const { data: configuration, isFetching } = useGetToolEnvironmentConfigurationQuery({
        dataProductId,
        id: toolId,
    });
    const [updateConfiguration, { isLoading: isSaving }] = useUpdateToolEnvironmentConfigurationMutation();
    const [draft, setDraft] = useState<Draft>({ base_values: {}, overrides: {} });

    useEffect(() => {
        if (configuration) {
            setDraft(toDraft(configuration));
        }
    }, [configuration]);

    const environments = configuration?.properties[0]?.environments ?? [];

    const setBaseValue = (property: string, value: string) =>
        setDraft((current) => ({ ...current, base_values: { ...current.base_values, [property]: value } }));

    const setOverride = (environmentId: string, property: string, value: string) =>
        setDraft((current) => {
            const { [property]: _removed, ...rest } = current.overrides[environmentId] ?? {};
            const values = value === INHERIT ? rest : { ...rest, [property]: value };
            return { ...current, overrides: { ...current.overrides, [environmentId]: values } };
        });

    const onSave = async () => {
        await updateConfiguration({
            dataProductId,
            id: toolId,
            updateToolEnvironmentConfigurationRequest: draft,
        }).unwrap();
        dispatchMessage({ content: t('Configuration saved'), type: 'success' });
    };

    const columns: TableColumnsType<OverridablePropertyConfiguration> = [
        { title: t('Property'), dataIndex: 'label' },
        {
            title: t('Base'),
            render: (_, property) => (
                <Select
                    disabled={!canEdit}
                    value={draft.base_values[property.name]}
                    options={property.allowed_values.map((value) => ({ label: value, value }))}
                    onChange={(value) => setBaseValue(property.name, value)}
                    popupMatchSelectWidth={false}
                />
            ),
        },
        ...environments.map((environment) => ({
            key: environment.id,
            title: environment.name,
            render: (_: unknown, property: OverridablePropertyConfiguration) => {
                const override = draft.overrides[environment.id]?.[property.name];
                return (
                    <Flex gap="small" align="center">
                        <Select
                            disabled={!canEdit}
                            value={override ?? INHERIT}
                            popupMatchSelectWidth={false}
                            options={[
                                {
                                    label: (
                                        <Typography.Text type="secondary">
                                            {t('Inherit')} ({draft.base_values[property.name]})
                                        </Typography.Text>
                                    ),
                                    value: INHERIT,
                                },
                                ...property.allowed_values.map((value) => ({ label: value, value })),
                            ]}
                            onChange={(value) => setOverride(environment.id, property.name, value)}
                        />
                        {override !== undefined && <Tag color="blue">{t('Override')}</Tag>}
                    </Flex>
                );
            },
        })),
    ];

    if (configuration && configuration.properties.length === 0) {
        return <Empty description={t('This Tool type has no overridable properties')} />;
    }

    return (
        <Flex vertical gap="middle">
            <Table<OverridablePropertyConfiguration>
                rowKey="name"
                columns={columns}
                dataSource={configuration?.properties}
                loading={isFetching}
                pagination={false}
            />
            {canEdit && (
                <Flex justify="flex-end">
                    <Button type="primary" onClick={onSave} loading={isSaving}>
                        {t('Save')}
                    </Button>
                </Flex>
            )}
        </Flex>
    );
}
