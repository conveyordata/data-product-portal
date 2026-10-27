import { generate } from '@ant-design/colors';
import { FastColor } from '@ant-design/fast-color';
import { type ThemeConfig, theme } from 'antd';

const { getDesignToken } = theme;

const token = getDesignToken();

const colorPrimary = '#543EDC';
const primaryPalette = generate(colorPrimary);
const primaryTint = (alpha: number) =>
    new FastColor(colorPrimary).setA(alpha).onBackground(token.colorBgContainer).toHexString();

const spacingTokens = {
    sizeUnit: 4,
    sizeStep: 4,
    marginSM: 16,
    margin: 24,
    marginMD: 24,
    marginLG: 32,
    marginXL: 32,
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
            colorPrimaryBg: colorPrimary,
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
            headerBorderRadius: 8,
            rowHoverBg: primaryTint(0.14),
            bodySortBg: primaryTint(0.04),
            headerSortActiveBg: primaryTint(0.1),
            rowSelectedBg: primaryPalette[2],
            rowSelectedHoverBg: primaryPalette[3],
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
        fontWeightStrong: 600,
        // -------- Brand Colors ---------
        // Primary
        colorPrimary,
        // Success
        colorSuccess: token.green6,
        colorSuccessBg: token.green1,
        colorSuccessBgHover: token.green2,
        colorSuccessBorder: token.green3,
        colorSuccessBorderHover: token.green4,
        colorSuccessHover: token.green4,
        colorSuccessActive: token.green7,
        colorSuccessText: token.green6,
        colorSuccessTextHover: token.green5,
        colorSuccessTextActive: token.green7,
        // Warning
        colorWarning: token.gold6,
        colorWarningBg: token.gold1,
        colorWarningBgHover: token.gold2,
        colorWarningBorder: token.gold3,
        colorWarningBorderHover: token.gold4,
        colorWarningHover: token.gold4,
        colorWarningActive: token.gold7,
        colorWarningText: token.gold6,
        colorWarningTextHover: token.gold5,
        colorWarningTextActive: token.gold7,
        // Info
        colorInfo: '#5B21B6',
        colorInfoBg: '#F5F3FF',
        colorInfoBgHover: token.colorPrimaryBgHover,
        colorInfoBorder: '#DDD6FE',
        colorInfoBorderHover: token.colorPrimaryBorderHover,
        colorInfoHover: token.colorPrimaryHover,
        colorInfoActive: token.colorPrimaryActive,
        colorInfoText: '#5B21B6',
        colorInfoTextHover: token.colorPrimaryTextHover,
        colorInfoTextActive: token.colorPrimaryTextActive,
        ...spacingTokens,
    },
    cssVar: {},
};

export { datamindedThemeConfig };
