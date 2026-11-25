import { FastColor } from '@ant-design/fast-color';
import { type ThemeConfig, theme } from 'antd';

const { getDesignToken } = theme;

const token = getDesignToken();

const colorPrimary = '#543EDC';
const primaryTint = (alpha: number) =>
    new FastColor(colorPrimary).setA(alpha).onBackground(token.colorBgContainer).toHexString();

const spacingTokens = {
    marginSM: 16,
    margin: 24,
    marginMD: 24,
    marginLG: 32,
    paddingSM: 16,
    padding: 24,
    paddingMD: 24,
    paddingLG: 32,
};

const datamindedThemeConfig: ThemeConfig = {
    components: {
        Layout: {
            siderBg: '#080635',
            bodyBg: '#FFF',
            headerBg: token.colorBgContainer,
        },
        Button: {
            borderRadius: 10,
            primaryShadow: 'none',
            dangerShadow: 'none', // Remove shadow from danger buttons to align with design
        },
        Menu: {
            darkItemBg: '#080635',
            itemBorderRadius: 10,
            darkPopupBg: '#080635',
            subMenuItemBorderRadius: 10,
            itemMarginInline: 5,
        },
        Select: {
            optionSelectedBg: 'transparent',
        },
        Table: {
            rowHoverBg: primaryTint(0.14),
            bodySortBg: primaryTint(0.04),
            headerSortActiveBg: primaryTint(0.1),
        },
        Input: {
            activeShadow: 'none',
        },
        Badge: {
            colorInfo: '#E6B14B',
        },
    },
    token: {
        fontFamily: 'DM Sans, sans-serif',
        // -------- Brand Colors ---------
        // Primary
        colorPrimary,
        // Info
        colorInfo: '#5B21B6',
        colorInfoBg: '#F5F3FF',
        colorInfoBorder: '#DDD6FE',
        colorInfoTextHover: token.colorPrimaryTextHover,
        ...spacingTokens,
    },
};

export { datamindedThemeConfig };
