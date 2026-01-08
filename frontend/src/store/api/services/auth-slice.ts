import type { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from '@reduxjs/toolkit';
import { api } from '@/store/api/services/generated/completeServiceApi.ts';
import type { User } from '@/store/api/services/generated/usersApi.ts';

type AuthState = {
    user?: User;
    isLoading: boolean;
};

const authSlice = createSlice({
    name: 'auth',
    initialState: { user: undefined, isLoading: true } as AuthState,
    reducers: {
        setCredentials: (
            state,
            {
                payload: { user },
            }: PayloadAction<{
                user?: User;
            }>,
        ) => {
            state.user = user;
            state.isLoading = false;
        },
    },
    extraReducers: (builder) => {
        builder.addMatcher(api.endpoints.getCurrentUser.matchFulfilled, (state, { payload }) => {
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
