import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

import { generateUUID } from '@/utils/uuid.helper.ts';

export type NotificationType = 'success' | 'info' | 'warning' | 'error';

export interface MessageState {
    id?: string;
    content?: string;
    duration?: number;
    onClose?: () => void;
    type: NotificationType;
}

export interface NotificationState {
    id?: string;
    message?: string;
    description?: string;
    type: NotificationType;
}

export interface ModalState {
    id?: string;
    isOpen: boolean;
}

export interface FeedbackState {
    notification: NotificationState;
    message: MessageState;
    modal: ModalState;
}

const initialState: FeedbackState = {
    message: {
        id: undefined,
        content: undefined,
        duration: undefined,
        onClose: undefined,
        type: 'info',
    },
    notification: {
        id: undefined,
        message: undefined,
        description: undefined,
        type: 'info',
    },
    modal: {
        id: undefined,
        isOpen: false,
    },
};

const feedbackSlice = createSlice({
    name: 'feedback',
    initialState,
    reducers: {
        showNotification(state, action: PayloadAction<NotificationState>) {
            state.notification.message = action.payload.message;
            state.notification.description = action.payload.description;
            state.notification.type = action.payload.type;
            state.notification.id = generateUUID();
        },
        showMessage(state, action: PayloadAction<MessageState>) {
            state.message.content = action.payload.content;
            state.message.duration = action.payload.duration;
            state.message.onClose = action.payload.onClose;
            state.message.type = action.payload.type;
            state.message.id = generateUUID();
        },
        showModal(state) {
            state.modal.isOpen = true;
            state.modal.id = generateUUID();
        },
        hideModal(state) {
            state.modal.isOpen = false;
        },
    },
    selectors: {
        selectMessage: (sliceState) => sliceState.message,
        selectNotification: (sliceState) => sliceState.notification,
        selectModal: (sliceState) => sliceState.modal,
    },
});

export const { showNotification, showMessage, showModal, hideModal } = feedbackSlice.actions;
export const { selectMessage, selectNotification, selectModal } = feedbackSlice.selectors;
export default feedbackSlice.reducer;
