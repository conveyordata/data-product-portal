import { ConfigProvider } from 'antd';
import { AppRoutes } from '@/routes.tsx';
import { AppConfig } from './config/app-config';

function App() {
    return (
        <ConfigProvider theme={AppConfig.getThemeConfiguration()}>
            <AppRoutes />
        </ConfigProvider>
    );
}

export default App;
