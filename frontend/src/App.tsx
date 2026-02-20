import { ConfigProvider } from 'antd';
import { BreadcrumbProvider } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { AppRoutes } from '@/routes.tsx';
import { AppConfig } from './config/app-config';

function App() {
    return (
        <ConfigProvider theme={AppConfig.getThemeConfiguration()}>
            <BreadcrumbProvider>
                <AppRoutes />
            </BreadcrumbProvider>
        </ConfigProvider>
    );
}

export default App;
