import { type PreloadedState, configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import { type RenderOptions, render } from '@testing-library/react';
import { NuqsTestingAdapter } from 'nuqs/adapters/testing';
import type { ReactElement, ReactNode } from 'react';
import { I18nextProvider } from 'react-i18next';
import { Provider } from 'react-redux';
import { MemoryRouter, type MemoryRouterProps } from 'react-router';
import { BreadcrumbProvider } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import authSlice from '@/store/api/services/auth-slice.ts';
import { api as generatedApiSlice } from '@/store/api/services/generated/completeServiceApi.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import cartSlice from '@/store/features/cart/cart-slice.ts';
import feedbackSlice from '@/store/features/feedback/feedback-slice.ts';
import wizardSlice from '@/store/features/wizard/wizard-slice.ts';
import i18n from './i18n';

const reducer = {
    auth: authSlice,
    cart: cartSlice,
    feedback: feedbackSlice,
    wizard: wizardSlice,
    [baseApiSlice.reducerPath]: baseApiSlice.reducer,
    [generatedApiSlice.reducerPath]: generatedApiSlice.reducer,
};

function createTestStore(preloadedState?: PreloadedState<any>) {
    const store = configureStore({
        reducer,
        preloadedState,
        middleware: (getDefaultMiddleware) =>
            getDefaultMiddleware().concat(baseApiSlice.middleware).concat(generatedApiSlice.middleware),
    });
    setupListeners(store.dispatch);
    return store;
}

type RenderWithProvidersOptions = Omit<RenderOptions, 'wrapper'> & {
    routerProps?: MemoryRouterProps;
    preloadedState?: PreloadedState<any>;
};

export function renderWithProviders(ui: ReactElement, options?: RenderWithProvidersOptions) {
    const { routerProps, preloadedState, ...renderOptions } = options ?? {};

    const Wrapper = ({children}: { children: ReactNode }) => {
        const store = createTestStore(preloadedState);
        return (
            <Provider store={store}>
                <I18nextProvider i18n={i18n}>
                    <BreadcrumbProvider>
                        <NuqsTestingAdapter>
                            {routerProps?
                                (<MemoryRouter {...routerProps}>{children}</MemoryRouter>):
                                (<>{children}</>)
                            }
                        </NuqsTestingAdapter>
                    </BreadcrumbProvider>
                </I18nextProvider>
            </Provider>
        );
    };
    return render(ui, {wrapper: Wrapper, ...renderOptions});
}

export { screen, waitFor, within } from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
