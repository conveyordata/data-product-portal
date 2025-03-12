import { notification } from 'antd';
import React, { useEffect } from 'react';
import { useSelector } from 'react-redux';

import { selectNotification } from '@/store/features/feedback/feedback-slice.ts';

const NotificationListener: React.FC = () => {
    const { message, description, type, id } = useSelector(selectNotification);
    const [notificationApi, contextHolder] = notification.useNotification({
        stack: { threshold: 3 },
        maxCount: 5,
    });

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
};

export default NotificationListener;
