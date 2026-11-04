import { SettingOutlined } from '@ant-design/icons';
import { Alert, Button, Flex, Space, Typography } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '@/components/empty-state/empty-state.component';
import { SettingsSectionHeader } from '@/pages/settings/components/settings-tabs/components/settings-section-header/settings-section-header.component';
import { dispatchMessage } from '@/utils/feedback';
import { EnvironmentChangesModal } from './environment-changes-modal.component';
import { EnvironmentSettingsMatrix } from './environment-settings-matrix.component';
import { type EnvironmentSettingsAsset, useEnvironmentSettings } from './use-environment-settings';

type Props = {
    dataProductId: string;
    technicalAsset: EnvironmentSettingsAsset;
    canEdit: boolean;
};

export function EnvironmentSettingsSection({ dataProductId, technicalAsset, canEdit }: Props) {
    const { t } = useTranslation();
    const settings = useEnvironmentSettings(dataProductId, technicalAsset);
    const [confirmOpen, setConfirmOpen] = useState(false);

    if (settings.metadata.length === 0) {
        return (
            <EmptyState
                icon={<SettingOutlined />}
                title={t('No Settings')}
                description={t('This type of Technical Asset has no settings.')}
            />
        );
    }

    const save = async () => {
        if (await settings.save()) {
            dispatchMessage({ content: t('Environment Settings saved'), type: 'success' });
        }
        setConfirmOpen(false);
    };

    return (
        <Flex vertical gap="middle">
            <SettingsSectionHeader
                title={t('Environment Settings')}
                description={
                    canEdit
                        ? t('Editable per Environment. Only Environments you changed are updated.')
                        : t('Each Environment keeps its own value.')
                }
            />
            <EnvironmentSettingsFields settings={settings} disabled={!canEdit || settings.isSaving} />
            {canEdit && (
                <Flex justify="space-between" align="center">
                    <Typography.Text type="secondary">
                        {settings.changedEnvironments.length === 0
                            ? t('No unsaved changes')
                            : t('Unsaved changes in {{environments}}', {
                                  environments: settings.changedEnvironments.map((e) => e.acronym).join(', '),
                              })}
                    </Typography.Text>
                    <Space>
                        <Button
                            disabled={settings.changedEnvironments.length === 0 || settings.isSaving}
                            onClick={settings.reset}
                        >
                            {t('Cancel')}
                        </Button>
                        <Button
                            type="primary"
                            disabled={settings.changedEnvironments.length === 0 || settings.errors.length > 0}
                            loading={settings.isValidating}
                            onClick={async () => {
                                if (await settings.validateNow()) setConfirmOpen(true);
                            }}
                        >
                            {t('Save')}
                        </Button>
                    </Space>
                </Flex>
            )}
            <EnvironmentChangesModal
                open={confirmOpen}
                environments={settings.environments}
                changes={settings.changes}
                loading={settings.isSaving}
                onConfirm={save}
                onCancel={() => setConfirmOpen(false)}
            />
        </Flex>
    );
}

export function EnvironmentSettingsFields({
    settings,
    disabled,
}: {
    settings: ReturnType<typeof useEnvironmentSettings>;
    disabled: boolean;
}) {
    const { t } = useTranslation();
    return (
        <>
            {settings.errors.length > 0 && (
                <Alert type="error" showIcon title={t('Some Environment Settings are not valid')} />
            )}
            <EnvironmentSettingsMatrix
                environments={settings.environments}
                metadata={settings.metadata}
                value={settings.values}
                onChange={settings.setValues}
                baseline={settings.stored}
                baselineNote={(value) => t('Was {{value}}', { value })}
                errors={settings.errors}
                disabled={disabled}
            />
        </>
    );
}
