import { type ThemeConfig, theme } from 'antd';

const { getDesignToken } = theme;

const token = getDesignToken();

const datamindedThemeConfig: ThemeConfig = {
    components: {
        Layout: {
            siderBg: '#080635',
            headerBg: token.colorBgContainer,
        },
        Menu: {
            darkItemBg: '#080635',
        },
    },
    token: {
        fontFamily: 'DM Sans, sans-serif',
        fontWeightStrong: 600,
        // -------- Brand Colors ---------
        // Primary
        colorPrimary: '#543EDC',
        // Info
        colorInfo: '#5B21B6',

    },
};


export { datamindedThemeConfig };
