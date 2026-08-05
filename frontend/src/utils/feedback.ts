import type { MessageInstance } from 'antd/es/message/interface';
import type { NotificationInstance } from 'antd/es/notification/interface';

export type FeedbackType = 'success' | 'info' | 'warning' | 'error';

export interface MessageOptions {
    content?: string;
    duration?: number;
    onClose?: () => void;
    type: FeedbackType;
}

export interface NotificationOptions {
    title?: string;
    description?: string;
    type: FeedbackType;
}

let messageApi: MessageInstance | null = null;
let notificationApi: NotificationInstance | null = null;

export function registerFeedbackApi(instances: { message: MessageInstance; notification: NotificationInstance }) {
    messageApi = instances.message;
    notificationApi = instances.notification;
}

export function unregisterFeedbackApi() {
    messageApi = null;
    notificationApi = null;
}

export function dispatchMessage({ content, duration, onClose, type }: MessageOptions) {
    if (!content) {
        return;
    }
    messageApi?.[type]({ content, duration, onClose });
}

export function dispatchNotification({ title, description, type }: NotificationOptions) {
    notificationApi?.[type]({ title, description, duration: false });
}
