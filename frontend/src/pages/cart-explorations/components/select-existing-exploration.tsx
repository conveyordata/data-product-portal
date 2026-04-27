import { Select, Space, Typography } from 'antd';
import { t } from 'i18next';

export const selectExistingExplorationItem = () => {
return <Select
    placeholder={t('Search Exploration')}
    showSearch={{
        optionFilterProp: 'label',
    }}
    autoFocus={isRestored && selectedExplorationId === undefined}
    defaultOpen={isRestored && selectedExplorationId === undefined}
    loading={isFetchingUserDataProducts}
    options={options}
    optionRender={(option) => (
        <Space vertical>
            <Typography.Text>{option.data.label}</Typography.Text>
            <Typography.Text type="secondary">{option.data.description}</Typography.Text>
        </Space>
    )}
/>
}