import '@/store/api/services/apiTags.ts';

import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import { useDispatch } from 'react-redux';
import authSlice from '@/store/api/services/auth-slice.ts';
import { api as generatedApiSlice } from '@/store/api/services/generated/completeServiceApi.ts';
import cartSlice from '@/store/features/cart/cart-slice.ts';
import wizardSlice from '@/store/features/wizard/wizard-slice.ts';
import { isDevMode } from '@/utils/env-mode.helper.ts';

const store = configureStore({
    reducer: {
        auth: authSlice,
        cart: cartSlice,
        wizard: wizardSlice,
        [generatedApiSlice.reducerPath]: generatedApiSlice.reducer,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(generatedApiSlice.middleware),
    devTools: isDevMode,
});

export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () => useDispatch<AppDispatch>();

setupListeners(store.dispatch);

export default store;
