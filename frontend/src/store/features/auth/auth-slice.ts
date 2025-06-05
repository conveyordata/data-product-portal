import type { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from '@reduxjs/toolkit';

import { authApiSlice } from '@/store/features/auth/auth-api-slice.ts';
import type { UserContract } from '@/types/users';

type AuthState = {
    user: UserContract | null;
    isLoading: boolean;
};

const authSlice = createSlice({
    name: 'auth',
    initialState: { user: null, isLoading: true } as AuthState,
    reducers: {
        setCredentials: (
            state,
            {
                payload: { user },
            }: PayloadAction<{
                user: UserContract | null;
            }>,
        ) => {
            state.user = user;
            state.isLoading = false;
        },
    },
    extraReducers: (builder) => {
        builder.addMatcher(authApiSlice.endpoints.authorize.matchFulfilled, (state, { payload }) => {
            state.user = payload;
            state.isLoading = false;
        });
    },
    selectors: {
        selectAuthState: (state) => state,
        selectCurrentUser: (state) => state.user,
    },
});

export const { setCredentials } = authSlice.actions;

export default authSlice.reducer;

export const { selectAuthState, selectCurrentUser } = authSlice.selectors;
