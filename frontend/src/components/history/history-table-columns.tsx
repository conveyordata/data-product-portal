import type { TableColumnsType } from 'antd';
import dayjs from 'dayjs';
import type { TFunction } from 'i18next';

import type { EventReferenceEntity } from '@/types/events/event-reference-entity';
import type { EventContract } from '@/types/events/event.contract';

import { HistoryTableEventName } from './history-table-event-name';

export interface HistoryColumnsProps {
    t: TFunction;
    resourceId: string;
    type: EventReferenceEntity;
}

export const getHistoryColumns = ({ t, resourceId, type }: HistoryColumnsProps): TableColumnsType<EventContract> => [
    {
        title: t('Event description'),
        key: 'Detail',
        render: (record: EventContract) => {
            return <HistoryTableEventName record={record} resourceId={resourceId} type={type} />;
        },
    },
    {
        title: t('Executed by'),
        dataIndex: 'actor',
        key: 'actor',
        width: '25%',
        render: (actor: { email: string }) => `${actor.email}`,
    },
    {
        title: t('Timestamp'),
        dataIndex: 'created_on',
        key: 'created_on',
        width: '20%',
        render: (created_on: string) => `${dayjs(created_on).format('YYYY-MM-DD HH:mm')} ${t('UTC')}`,
    },
];
