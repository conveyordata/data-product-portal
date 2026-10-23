import { Collapse, Empty, Flex, Tabs, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { useGetEnvironmentsQuery } from '@/store/api/services/generated/configurationEnvironmentsApi.ts';
import { PlatformTypeKind, useGetAllPlatformsQuery } from '@/store/api/services/generated/configurationPlatformsApi.ts';
import { PlatformEnvironmentSettingsEditor } from './platform-environment-settings-editor.tsx';

export function PlatformTab() {
    const { t } = useTranslation();
    const { data: { platforms = [] } = {}, isFetching } = useGetAllPlatformsQuery();
    const { data: { environments = [] } = {} } = useGetEnvironmentsQuery();

    if (!isFetching && platforms.length === 0) {
        return <Empty description={t('No platforms installed')} />;
    }

    return (
        <Collapse
            items={platforms.map((platform) => ({
                key: platform.key,
                label: (
                    <Flex gap="small" align="center" wrap>
                        <Typography.Text strong>{platform.display_name}</Typography.Text>
                        {platform.types.map((type) => (
                            <Tag key={type.name} color={type.kind === PlatformTypeKind.Tool ? 'purple' : 'blue'}>
                                {type.kind === PlatformTypeKind.Tool ? t('Tool') : t('Asset')}: {type.display_name}
                            </Tag>
                        ))}
                    </Flex>
                ),
                children: platform.has_environments ? (
                    <Tabs
                        destroyOnHidden
                        items={environments.map((environment) => ({
                            key: environment.id,
                            label: environment.name,
                            children: (
                                <PlatformEnvironmentSettingsEditor
                                    platformKey={platform.key}
                                    environmentId={environment.id}
                                />
                            ),
                        }))}
                    />
                ) : (
                    <Typography.Text type="secondary">{t('This platform has no environment settings')}</Typography.Text>
                ),
            }))}
        />
    );
}
