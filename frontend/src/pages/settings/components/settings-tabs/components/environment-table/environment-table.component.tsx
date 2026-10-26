import { CloudServerOutlined } from '@ant-design/icons';
import { Flex, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { ListTable } from '@/components/list-table/list-table.component.tsx';

import {
    type EnvironmentGetItem,
    useGetEnvironmentsQuery,
    useUpdateEnvironmentIsGlobalMutation,
} from '@/store/api/services/generated/configurationEnvironmentsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { getEnvironmentTableColumns } from './environment-table-columns';

export function EnvironmentTable() {
    const { t } = useTranslation();
    const environmentsQuery = useGetEnvironmentsQuery();
    const { data, refetch } = environmentsQuery;
    const [updateIsGlobal, { isLoading: isUpdating }] = useUpdateEnvironmentIsGlobalMutation();

    const handleToggleGlobal = async (environment: EnvironmentGetItem, isGlobal: boolean) => {
        try {
            await updateIsGlobal({ id: environment.id, environmentUpdateGlobal: { is_global: isGlobal } }).unwrap();
            refetch();
        } catch (_e) {
            dispatchMessage({ content: t('Failed to update environment'), type: 'error' });
        }
    };

    const columns = getEnvironmentTableColumns({ t, onToggleGlobal: handleToggleGlobal });

    return (
        <Flex vertical gap="large">
            <Typography.Title level={3}>{t('Environments')}</Typography.Title>
            <ListTable<EnvironmentGetItem>
                query={environmentsQuery}
                dataSource={data?.environments ?? []}
                columns={columns}
                subject={t('environments')}
                emptyState={{
                    icon: <CloudServerOutlined />,
                    title: t('No environments yet'),
                    description: t('Environments are the places data lands, such as development and production.'),
                }}
                loading={isUpdating}
                rowKey={(record) => record.id}
                rowHoverable
                size="small"
            />
        </Flex>
    );
}
