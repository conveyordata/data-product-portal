import { Button, Flex, Input } from 'antd';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    useGetPlatformEnvironmentSettingsQuery,
    useUpdatePlatformEnvironmentSettingsMutation,
} from '@/store/api/services/generated/configurationPlatformsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';

type Props = {
    platformKey: string;
    environmentId: string;
};

export function PlatformEnvironmentSettingsEditor({ platformKey, environmentId }: Props) {
    const { t } = useTranslation();
    const { data, isFetching } = useGetPlatformEnvironmentSettingsQuery({ platformKey, environmentId });
    const [updateSettings, { isLoading }] = useUpdatePlatformEnvironmentSettingsMutation();
    const [text, setText] = useState('');

    useEffect(() => {
        if (data) {
            setText(JSON.stringify(data.settings, null, 2));
        }
    }, [data]);

    const onSave = async () => {
        let settings: Record<string, unknown>;
        try {
            settings = JSON.parse(text);
        } catch {
            dispatchMessage({ content: t('The settings are not valid JSON'), type: 'error' });
            return;
        }
        await updateSettings({ platformKey, environmentId, settings }).unwrap();
        dispatchMessage({ content: t('Platform settings saved'), type: 'success' });
    };

    return (
        <Flex vertical gap="small">
            <Input.TextArea
                value={text}
                onChange={(event) => setText(event.target.value)}
                autoSize={{ minRows: 6, maxRows: 30 }}
                disabled={isFetching}
                spellCheck={false}
            />
            <Flex justify="flex-end">
                <Button type="primary" onClick={onSave} loading={isLoading} disabled={isFetching}>
                    {t('Save')}
                </Button>
            </Flex>
        </Flex>
    );
}
