import { ConfigProvider } from 'antd';
import { FeedbackBridge } from '@/components/feedback/feedback-bridge.component.tsx';
import { BreadcrumbProvider } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { AppRoutes } from '@/routes.tsx';
import {datamindedThemeConfig} from "@/theme/antd-theme.ts";

function App() {
    return (
        <ConfigProvider theme={datamindedThemeConfig}>
            <FeedbackBridge />
            <BreadcrumbProvider>
                <AppRoutes />
            </BreadcrumbProvider>
        </ConfigProvider>
    );
}

export default App;
