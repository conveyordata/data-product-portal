import type { TableColumnsType } from 'antd';
import { Typography } from 'antd';
import dayjs from 'dayjs';
import type { TFunction } from 'i18next';

import { EventContract } from '@/types/events/event.contract';
import { getTargetDisplayLabel } from '@/utils/history.helper';

export interface HistoryColumnsProps {
    t: TFunction;
}

export const getHistoryColumns = ({ t }: HistoryColumnsProps): TableColumnsType<EventContract> => [
    {
        title: t('Event name'),
        dataIndex: 'name',
        key: 'name',
        width: '30%',
        render: (event: string) => t(event) || t('No title available'),
    },
    {
        title: t('Involved entities'),
        key: 'Detail',
        width: '25%',
        render: (record: EventContract) => {
            const targetLabel = getTargetDisplayLabel(t, record);

            if (targetLabel) {
                return <Typography.Text>{targetLabel}</Typography.Text>;
            }
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
