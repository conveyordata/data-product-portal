import { ConfigProvider } from 'antd';

import { AppRoutes } from '@/routes.tsx';
import { conveyorThemeConfig } from '@/theme/antd-theme.ts';

function App() {
    return (
        <ConfigProvider theme={conveyorThemeConfig}>
            <AppRoutes />
        </ConfigProvider>
    );
}

export default App;
