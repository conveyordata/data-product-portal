import type { TableColumnsType } from 'antd';
import dayjs from 'dayjs';
import type { TFunction } from 'i18next';

import { EventContract } from '@/types/events/event.contract';
import { EventReferenceEntity } from '@/types/events/event-reference-entity';
import { EventType } from '@/types/events/event-types';
import { getEventTypeDisplayName } from '@/utils/history.helper';

import { HistoryTableLink } from './history-table-link';

export interface HistoryColumnsProps {
    t: TFunction;
    resourceId: string;
    type: EventReferenceEntity;
}

export const getHistoryColumns = ({ t, resourceId, type }: HistoryColumnsProps): TableColumnsType<EventContract> => [
    {
        title: t('Event name'),
        dataIndex: 'name',
        key: 'name',
        width: '30%',
        render: (name: EventType) => getEventTypeDisplayName(t, name) || t('No title available'),
    },
    {
        title: t('External involved entity'),
        key: 'Detail',
        width: '25%',
        render: (record: EventContract) => {
            return <HistoryTableLink record={record} resourceId={resourceId} type={type} />;
        },
    },
    {
        title: t('Executed by'),
        dataIndex: 'actor',
        key: 'actor',

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
