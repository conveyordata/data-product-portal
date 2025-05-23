import { ConfigProvider } from 'antd';

import { AppRoutes } from '@/routes.tsx';
import { datamindedThemeConfig } from '@/theme/antd-theme.ts';

function App() {
    return (
        <ConfigProvider theme={datamindedThemeConfig}>
            <AppRoutes />
        </ConfigProvider>
    );
}

export default App;
