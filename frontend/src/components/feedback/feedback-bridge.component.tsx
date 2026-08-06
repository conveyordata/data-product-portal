import { message, notification } from 'antd';
import { useEffect } from 'react';
import { registerFeedbackApi, unregisterFeedbackApi } from '@/utils/feedback.ts';

export function FeedbackBridge() {
    const [messageApi, messageContextHolder] = message.useMessage({ maxCount: 5 });
    const [notificationApi, notificationContextHolder] = notification.useNotification({
        maxCount: 5,
        stack: { threshold: 3 },
    });

    useEffect(() => {
        registerFeedbackApi({ message: messageApi, notification: notificationApi });
        return unregisterFeedbackApi;
    }, [messageApi, notificationApi]);

    return (
        <>
            {messageContextHolder}
            {notificationContextHolder}
        </>
    );
}
