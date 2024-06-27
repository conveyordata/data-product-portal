import { configureStore } from '@reduxjs/toolkit';
import { useDispatch } from 'react-redux';
import feedbackSlice from '@/store/features/feedback/feedback-slice.ts';
import { setupListeners } from '@reduxjs/toolkit/query';
import { isDevMode } from '@/utils/env-mode.helper.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import authSlice from '@/store/features/auth/auth-slice.ts';

const store = configureStore({
    reducer: {
        feedback: feedbackSlice,
        auth: authSlice,
        [baseApiSlice.reducerPath]: baseApiSlice.reducer,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(baseApiSlice.middleware),
    devTools: isDevMode,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector = (selector: (state: RootState) => unknown) => selector(store.getState());

setupListeners(store.dispatch);

export default store;
