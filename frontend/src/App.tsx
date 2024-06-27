import { ConfigProvider } from 'antd';
import { AppRoutes } from '@/routes.tsx';
import { greenThemeConfig } from '@/theme/antd-theme.ts';

function App() {
    return (
        <ConfigProvider theme={greenThemeConfig}>
            <AppRoutes />
        </ConfigProvider>
    );
}

export default App;
