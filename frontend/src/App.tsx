import { ConfigProvider } from 'antd';
import { FeedbackBridge } from '@/components/feedback/feedback-bridge.component.tsx';
import { BreadcrumbProvider } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { AppRoutes } from '@/routes.tsx';
import { AppConfig } from './config/app-config';

function App() {
    return (
        <ConfigProvider theme={AppConfig.getThemeConfiguration()}>
            <FeedbackBridge />
            <BreadcrumbProvider>
                <AppRoutes />
            </BreadcrumbProvider>
        </ConfigProvider>
    );
}

export default App;
