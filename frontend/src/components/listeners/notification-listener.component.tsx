import { notification } from 'antd';
import { useEffect } from 'react';
import { useSelector } from 'react-redux';

import { selectNotification } from '@/store/features/feedback/feedback-slice.ts';

export default function NotificationListener() {
    const { message, description, type, id } = useSelector(selectNotification);
    const [notificationApi, contextHolder] = notification.useNotification({
        stack: { threshold: 3 },
        maxCount: 5,
    });

    // biome-ignore lint: I don't know what the effect of removing id is
    useEffect(() => {
        if (message && description) {
            notificationApi[type]({
                message,
                description,
                duration: null,
            });
        }
    }, [message, description, type, id, notificationApi]);

    return <>{contextHolder}</>;
}
