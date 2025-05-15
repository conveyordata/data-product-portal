import { CaretRightOutlined } from '@ant-design/icons';
import type { TableColumnsType } from 'antd';
import { Flex, Typography } from 'antd';
import dayjs from 'dayjs';
import type { TFunction } from 'i18next';

import { EventContract } from '@/types/events/event.contract';
import { getSubjectDisplayLabel, getTargetDisplayLabel } from '@/utils/history.helper';

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
        width: '30%',
        render: (record: EventContract) => {
            const subjectLabel = getSubjectDisplayLabel(t, record);
            const targetLabel = getTargetDisplayLabel(t, record);

            if (targetLabel) {
                return (
                    <Flex vertical>
                        <Typography.Text>{subjectLabel}</Typography.Text>
                        <Typography.Text>
                            <CaretRightOutlined /> {targetLabel}
                        </Typography.Text>
                    </Flex>
                );
            }
            return <Typography.Text>{subjectLabel}</Typography.Text>;
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
        width: '15%',
        render: (created_on: string) => `${dayjs(created_on).format('YYYY-MM-DD HH:mm')} ${t('UTC')}`,
    },
];
