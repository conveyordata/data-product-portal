import { AppRoutes } from '@/routes.tsx';
import { ConfigProvider } from 'antd';
import { AppConfig } from './config/app-config';

function App() {
    return (
        <ConfigProvider theme={AppConfig.getThemeConfiguration()}>
            <AppRoutes />
        </ConfigProvider>
    );
}

export default App;
