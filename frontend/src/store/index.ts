import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import { useDispatch } from 'react-redux';
import { api as generatedApiSlice } from '@/store/api/services/generated/completeServiceApi.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import authSlice from '@/store/features/auth/auth-slice.ts';
import cartSlice from '@/store/features/cart/cart-slice.ts';
import feedbackSlice from '@/store/features/feedback/feedback-slice.ts';
import { isDevMode } from '@/utils/env-mode.helper.ts';

const store = configureStore({
    reducer: {
        feedback: feedbackSlice,
        auth: authSlice,
        cart: cartSlice,
        [baseApiSlice.reducerPath]: baseApiSlice.reducer,
        [generatedApiSlice.reducerPath]: generatedApiSlice.reducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware().concat(baseApiSlice.middleware).concat(generatedApiSlice.middleware),
    devTools: isDevMode,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector = (selector: (state: RootState) => unknown) => selector(store.getState());

setupListeners(store.dispatch);

export default store;
