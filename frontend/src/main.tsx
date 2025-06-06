import '@/styles/_globals.scss';
import './i18n.ts';
import '@ant-design/v5-patch-for-react-19';

import React, { Suspense } from 'react';
import ReactDOM from 'react-dom/client';
import { I18nextProvider } from 'react-i18next';
import { AuthProvider } from 'react-oidc-context';
import { Provider } from 'react-redux';

import MessageListener from '@/components/listeners/message-listener.component.tsx';
import NotificationListener from '@/components/listeners/notification-listener.component.tsx';
import { oidcAuthProviderProps } from '@/config/oidc-config.ts';
import i18n from '@/i18n';
import store from '@/store';

import App from './App.tsx';

const root = document.getElementById('root');
if (!root) {
    throw new Error('Root is missing');
}

ReactDOM.createRoot(root).render(
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
