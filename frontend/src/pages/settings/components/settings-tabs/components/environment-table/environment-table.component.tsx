import { CloudServerOutlined } from '@ant-design/icons';
import { Flex, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { ListTable } from '@/components/list-table/list-table.component.tsx';

import {
    type EnvironmentGetItem,
    useGetEnvironmentsQuery,
    useUpdateEnvironmentMutation,
} from '@/store/api/services/generated/configurationEnvironmentsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { getEnvironmentTableColumns } from './environment-table-columns';

export function EnvironmentTable() {
    const { t } = useTranslation();
    const environmentsQuery = useGetEnvironmentsQuery();
    const { data, refetch } = environmentsQuery;
    const [updateEnvironment, { isLoading: isUpdating }] = useUpdateEnvironmentMutation();

    const handleChangePosition = async (environment: EnvironmentGetItem, position: number | null) => {
        try {
            await updateEnvironment({ id: environment.id, environmentUpdate: { position } }).unwrap();
            refetch();
        } catch (_e) {
            dispatchMessage({ content: t('Failed to update environment'), type: 'error' });
        }
    };

    const handleToggleGlobal = async (environment: EnvironmentGetItem, isGlobal: boolean) => {
        try {
            await updateEnvironment({ id: environment.id, environmentUpdate: { is_global: isGlobal } }).unwrap();
            refetch();
        } catch (_e) {
            dispatchMessage({ content: t('Failed to update environment'), type: 'error' });
        }
    };

    const columns = getEnvironmentTableColumns({
        t,
        onToggleGlobal: handleToggleGlobal,
        onChangePosition: handleChangePosition,
        disabled: isUpdating || isUpdating,
    });

    return (
        <Flex vertical gap="large">
            <Typography.Title level={3}>{t('Environments')}</Typography.Title>
            <ListTable<EnvironmentGetItem>
                query={environmentsQuery}
                dataSource={data?.environments ?? []}
                columns={columns}
                subject={t('Environments')}
                emptyState={{
                    icon: <CloudServerOutlined />,
                    title: t('No Environments yet'),
                    description: t('Environments are the places data lands, such as development and production.'),
                }}
                loading={isUpdating || isUpdating}
                rowKey={(record) => record.id}
                rowHoverable
                size="small"
            />
        </Flex>
    );
}
