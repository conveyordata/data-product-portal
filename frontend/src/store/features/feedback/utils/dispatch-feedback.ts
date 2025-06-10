import store from '@/store';
import {
    type MessageState,
    type NotificationState,
    hideModal,
    showMessage,
    showModal,
    showNotification,
} from '@/store/features/feedback/feedback-slice.ts';

export function dispatchNotification({ message, description, type }: NotificationState) {
    store.dispatch(showNotification({ message, description, type }));
}

export function dispatchMessage({ content, duration, onClose, type }: MessageState) {
    store.dispatch(showMessage({ content, duration, onClose, type }));
}

export function dispatchShowModal() {
    store.dispatch(showModal());
}

export function dispatchHideModal() {
    store.dispatch(hideModal());
}
