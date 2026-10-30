import { DeleteOutlined, NotificationOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, Flex, Input, Popconfirm, type TableColumnsType, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { ANNOUNCEMENT_URGENCY, AnnouncementTypeIcon } from '@/components/announcements/announcement-type.tsx';
import {
    EmptyState,
    emptyStateQueryProps,
    isAwaitingData,
    searchFilter,
} from '@/components/empty-state/empty-state.component.tsx';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { DEFAULT_TABLE_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { TabKeys } from '@/pages/output-port/components/dataset-tabs/dataset-tabkeys';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type Announcement,
    type AnnouncementType,
    useGetOutputPortAnnouncementsQuery,
    useRemoveOutputPortAnnouncementMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import {
    InputPortStatus,
    useGetInputPortsForOutputPortQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { formatDateFromISOString } from '@/utils/date.helper.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { linkify } from '@/utils/linkify.tsx';
import { cleanupForSearching } from '@/utils/search.ts';
import { Sorter } from '@/utils/table-sorter.helper';
import { NewAnnouncementModal } from './new-announcement-modal.tsx';

type Props = {
    outputPortId: string;
    dataProductId: string;
};

export function AnnouncementsTab({ outputPortId, dataProductId }: Props) {
    const { t } = useTranslation();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const announcementsQuery = useGetOutputPortAnnouncementsQuery({ id: outputPortId, dataProductId });
    const { data: { announcements = [] } = {} } = announcementsQuery;
    const { data: { allowed: canPost = false } = {} } = useCheckAccessQuery({
        resource: outputPortId,
        action: AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES,
    });
    const { data: { input_ports: inputPorts = [] } = {} } = useGetInputPortsForOutputPortQuery(
        { outputPortId, dataProductId },
        { skip: !canPost },
    );
    const consumerCount = inputPorts.filter(({ status }) => status === InputPortStatus.Approved).length;
    const filteredAnnouncements = useMemo(() => {
        const search = cleanupForSearching(searchTerm);
        return announcements.filter(({ title, message }) =>
            cleanupForSearching(`${title} ${message}`).includes(search),
        );
    }, [announcements, searchTerm]);
    const { pagination, handlePaginationChange } = useTablePagination(filteredAnnouncements, {
        initialPagination: DEFAULT_TABLE_PAGINATION,
    });

    const columns = useMemo((): TableColumnsType<Announcement> => {
        const sorter = new Sorter<Announcement>();
        return [
            {
                title: t('Type'),
                dataIndex: 'type',
                width: 72,
                align: 'center',
                render: (type: AnnouncementType) => <AnnouncementTypeIcon type={type} />,
                sorter: sorter.numberSorter(({ type }) => ANNOUNCEMENT_URGENCY.indexOf(type)),
            },
            {
                title: t('Announcement'),
                dataIndex: 'title',
                render: (_, { title, message }) => (
                    <Flex vertical>
                        <Typography.Text strong>{title}</Typography.Text>
                        <Typography.Paragraph
                            type="secondary"
                            style={{ whiteSpace: 'pre-line', marginBottom: 0 }}
                            ellipsis={{
                                rows: 2,
                                expandable: 'collapsible',
                                symbol: (expanded) => (expanded ? t('less') : t('more')),
                            }}
                        >
                            {linkify(message)}
                        </Typography.Paragraph>
                    </Flex>
                ),
            },
            {
                title: t('Posted'),
                dataIndex: 'created_at',
                width: 180,
                defaultSortOrder: 'descend',
                sorter: sorter.stringSorter(({ created_at }) => created_at),
                render: (_, { created_at, author }) => (
                    <Flex vertical>
                        <Typography.Text>{formatDateFromISOString(created_at)}</Typography.Text>
                        <Typography.Text type="secondary">
                            {author ? `${author.first_name} ${author.last_name}` : t('a former user')}
                        </Typography.Text>
                    </Flex>
                ),
            },
            {
                title: t('Actions'),
                key: 'actions',
                width: 110,
                hidden: !canPost,
                render: (_, announcement) => (
                    <DeleteAnnouncementButton announcement={announcement} dataProductId={dataProductId} />
                ),
            },
        ];
    }, [t, canPost, dataProductId]);

    if (isAwaitingData(announcementsQuery)) {
        return <LoadingSpinner />;
    }

    const newAnnouncementButton = canPost && (
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            {t('New Announcement')}
        </Button>
    );

    return (
        <Flex vertical gap="middle">
            {announcements.length === 0 ? (
                <EmptyState
                    icon={<NotificationOutlined />}
                    title={t('No announcements yet')}
                    description={
                        canPost ? (
                            <Trans
                                t={t}
                                i18nKey="AnnouncementsEmptyProducer"
                                count={consumerCount}
                                defaults="Post one to tell every Consuming Data Product about an issue, a change they need to make, planned maintenance or a new version. <link>{{count}} consumers</link> use this Output Port today."
                                components={{ link: <Link to={{ search: `?tab=${TabKeys.Consumers}` }} /> }}
                            />
                        ) : (
                            t(
                                "The team that owns this Output Port hasn't posted any updates. When they do, Consuming Data Products get a notification.",
                            )
                        )
                    }
                    action={newAnnouncementButton}
                    {...emptyStateQueryProps(announcementsQuery)}
                />
            ) : (
                <>
                    <Flex gap="middle">
                        <Input.Search
                            placeholder={t('Search announcements by title or message')}
                            allowClear
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                        {newAnnouncementButton}
                    </Flex>
                    <ListTable<Announcement>
                        query={announcementsQuery}
                        dataSource={filteredAnnouncements}
                        columns={columns}
                        subject={t('announcements')}
                        emptyState={{ icon: <NotificationOutlined />, title: t('No announcements yet') }}
                        filter={searchFilter(searchTerm, setSearchTerm)}
                        rowKey={({ id }) => id}
                        onChange={handlePaginationChange}
                        pagination={{
                            ...pagination,
                            size: 'small',
                            placement: ['bottomEnd'],
                            showTotal: (total, range) =>
                                t('Showing {{range0}}-{{range1}} of {{count}} announcements', {
                                    range0: range[0],
                                    range1: range[1],
                                    count: total,
                                }),
                        }}
                        size="small"
                    />
                </>
            )}
            {isModalOpen && (
                <NewAnnouncementModal
                    dataProductId={dataProductId}
                    outputPortId={outputPortId}
                    consumerCount={consumerCount}
                    onClose={() => setIsModalOpen(false)}
                />
            )}
        </Flex>
    );
}

function DeleteAnnouncementButton({
    announcement,
    dataProductId,
}: {
    announcement: Announcement;
    dataProductId: string;
}) {
    const { t } = useTranslation();
    const [removeAnnouncement, { isLoading }] = useRemoveOutputPortAnnouncementMutation();

    const onDelete = async () => {
        try {
            await removeAnnouncement({
                dataProductId,
                id: announcement.output_port_id,
                announcementId: announcement.id,
            }).unwrap();
            dispatchMessage({ content: t('Announcement deleted'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Could not delete announcement'), type: 'error' });
        }
    };

    return (
        <Popconfirm
            title={t('Delete Announcement')}
            description={t(
                'Consumers will no longer see it. The deletion is recorded in History. This cannot be undone.',
            )}
            okText={t('Delete')}
            okButtonProps={{ danger: true, loading: isLoading }}
            cancelText={t('Cancel')}
            onConfirm={onDelete}
        >
            <Button size="small" type="link" danger icon={<DeleteOutlined />}>
                {t('Delete')}
            </Button>
        </Popconfirm>
    );
}
