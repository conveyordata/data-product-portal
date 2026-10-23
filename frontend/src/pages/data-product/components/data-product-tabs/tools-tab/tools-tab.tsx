import { PlusOutlined } from '@ant-design/icons';
import { Button, Flex, Popconfirm, Table, type TableColumnsType } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { useModal } from '@/hooks/use-modal.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { useGetAllPlatformsQuery } from '@/store/api/services/generated/configurationPlatformsApi.ts';
import {
    type Tool,
    useDeleteToolMutation,
    useGetDataProductToolsQuery,
} from '@/store/api/services/generated/dataProductsToolsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { createToolIdPath } from '@/types/navigation.ts';
import { CreateToolModal } from './create-tool-modal.tsx';

type Props = {
    dataProductId: string;
};

export function ToolsTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { isVisible, handleOpen, handleClose } = useModal();
    const { data: { tools = [] } = {}, isFetching } = useGetDataProductToolsQuery(dataProductId);
    const { data: { platforms = [] } = {} } = useGetAllPlatformsQuery();
    const [deleteTool, { isLoading: isDeleting }] = useDeleteToolMutation();
    const { data: access } = useCheckAccessQuery({
        resource: dataProductId,
        action: AuthorizationAction.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET,
    });
    const canEdit = access?.allowed ?? false;

    const columns: TableColumnsType<Tool> = useMemo(
        () => [
            {
                title: t('Name'),
                dataIndex: 'name',
                render: (name: string, tool) => <Link to={createToolIdPath(tool.id, dataProductId)}>{name}</Link>,
            },
            {
                title: t('Type'),
                render: (_, tool) => {
                    const platform = platforms.find((p) => p.key === tool.platform_key);
                    const type = platform?.types.find((tp) => tp.name === tool.tool_type);
                    return `${platform?.display_name ?? tool.platform_key} · ${type?.display_name ?? tool.tool_type}`;
                },
            },
            { title: t('Description'), dataIndex: 'description' },
            {
                title: t('Actions'),
                render: (_, tool) =>
                    canEdit && (
                        <Popconfirm
                            title={t('Delete Tool')}
                            description={t('Are you sure you want to delete this Tool?')}
                            onConfirm={() => deleteTool({ dataProductId, id: tool.id })}
                        >
                            <Button type="link" disabled={isDeleting}>
                                {t('Delete')}
                            </Button>
                        </Popconfirm>
                    ),
            },
        ],
        [t, platforms, canEdit, deleteTool, dataProductId, isDeleting],
    );

    return (
        <Flex vertical gap="middle">
            {canEdit && (
                <Flex justify="flex-end">
                    <Button type="primary" icon={<PlusOutlined />} onClick={handleOpen}>
                        {t('Create Tool')}
                    </Button>
                </Flex>
            )}
            <Table<Tool> rowKey="id" columns={columns} dataSource={tools} loading={isFetching} pagination={false} />
            {isVisible && <CreateToolModal dataProductId={dataProductId} onClose={handleClose} />}
        </Flex>
    );
}
