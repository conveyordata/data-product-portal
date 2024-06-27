import React, { Suspense } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import '@/styles/_globals.scss';
import './i18n.ts';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/i18n';
import { Provider } from 'react-redux';
import store from '@/store';
import NotificationListener from '@/components/listeners/notification-listener.component.tsx';
import MessageListener from '@/components/listeners/message-listener.component.tsx';
import { AuthProvider } from 'react-oidc-context';
import { oidcAuthProviderProps } from '@/config/oidc-config.ts';

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <AuthProvider {...oidcAuthProviderProps}>
            <Provider store={store}>
                <I18nextProvider i18n={i18n}>
                    <Suspense fallback={''}>
                        <MessageListener />
                        <NotificationListener />
                        <App />
                    </Suspense>
                </I18nextProvider>
            </Provider>
        </AuthProvider>
    </React.StrictMode>,
);
