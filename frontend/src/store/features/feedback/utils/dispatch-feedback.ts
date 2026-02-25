import store from '@/store';
import { type MessageState, showMessage } from '@/store/features/feedback/feedback-slice.ts';

export function dispatchMessage({ content, duration, onClose, type }: MessageState) {
    store.dispatch(showMessage({ content, duration, onClose, type }));
}
