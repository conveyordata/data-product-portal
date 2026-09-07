import { Flex, Table, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

import {
    type EnvironmentGetItem,
    useGetEnvironmentsQuery,
    useUpdateEnvironmentIsGlobalMutation,
} from '@/store/api/services/generated/configurationEnvironmentsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { getEnvironmentTableColumns } from './environment-table-columns';

export function EnvironmentTable() {
    const { t } = useTranslation();
    const { data, isFetching, refetch } = useGetEnvironmentsQuery();
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
            <Table<EnvironmentGetItem>
                dataSource={data?.environments ?? []}
                columns={columns}
                rowKey={(record) => record.id}
                loading={isFetching || isUpdating}
                rowHoverable
                size="small"
            />
        </Flex>
    );
}
