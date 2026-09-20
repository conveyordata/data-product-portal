import { type ThemeConfig, theme } from 'antd';

const { getDesignToken } = theme;

const token = getDesignToken();

// Borders must stay legible on projectors and external screens, where the antd
// defaults (#d9d9d9 and #f0f0f0) wash out to nothing.
const borderTokens = {
    colorBorder: '#8c8c8c',
    colorBorderSecondary: '#bfbfbf',
};

// Placeholders, empty states and secondary labels are real text and have to be
// readable. The antd defaults reach 1.8:1 against white for placeholders and
// 3.4:1 for descriptions, which is why "Search by name", "Filter by role" and
// "No data" disappear on an external screen. These clear 4.5:1. Disabled text
// stays deliberately faint: it must still read as unavailable.
const textTokens = {
    colorTextPlaceholder: 'rgba(0, 0, 0, 0.55)',
    colorTextTertiary: 'rgba(0, 0, 0, 0.55)',
    colorTextDescription: 'rgba(0, 0, 0, 0.55)',
    colorTextDisabled: 'rgba(0, 0, 0, 0.45)',
};

// Popups float on the same white as the page behind them, so the shadow is the
// only thing separating a dropdown from the form underneath it. Roughly double
// the antd opacity and tint it with each theme's own dark, so a dropdown reads
// as lifted rather than dissolving into the form.
const elevationTokens = (tint: string) => ({
    boxShadowSecondary: [
        `0 6px 16px 0 rgba(${tint}, 0.16)`,
        `0 3px 6px -4px rgba(${tint}, 0.24)`,
        `0 9px 28px 8px rgba(${tint}, 0.10)`,
    ].join(', '),
});

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

const blueThemeConfig: ThemeConfig = {
    components: {
        Layout: {
            headerBg: token.colorBgContainer,
        },
        Typography: {
            margin: 0,
            titleMarginBottom: 0,
            titleMarginTop: 0,
        },
        Button: {
            defaultBorderColor: token.colorPrimaryBorder,
            defaultColor: token.colorPrimaryText,
        },
        Table: {
            rowHoverBg: token.blue1,
            headerSortActiveBg: token.blue1,
            headerSortHoverBg: token.blue2,
            bodySortBg: token.blue1,
        },
    },
    token: {
        fontFamily: 'SF Pro Text, sans-serif',
        fontWeightStrong: 600,
        // -------- Brand Colors ---------
        // Primary
        colorPrimary: token.blue6,
        colorPrimaryBg: token.blue1,
        colorPrimaryBgHover: token.blue2,
        colorPrimaryBorder: token.blue3,
        colorPrimaryBorderHover: token.blue4,
        colorPrimaryHover: token.blue5,
        colorPrimaryActive: token.blue7,
        colorPrimaryText: token.blue6,
        colorPrimaryTextHover: token.blue5,
        colorPrimaryTextActive: token.blue7,
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
        colorInfo: token.colorPrimary,
        colorInfoBg: token.colorPrimaryBg,
        colorInfoBgHover: token.colorPrimaryBgHover,
        colorInfoBorder: token.colorPrimaryBorder,
        colorInfoBorderHover: token.colorPrimaryBorderHover,
        colorInfoHover: token.colorPrimaryHover,
        colorInfoActive: token.colorPrimaryActive,
        colorInfoText: token.colorPrimaryText,
        colorInfoTextHover: token.colorPrimaryTextHover,
        colorInfoTextActive: token.colorPrimaryTextActive,
        ...spacingTokens,
        ...borderTokens,
        ...textTokens,
        ...elevationTokens('0, 0, 0'),
    },
    cssVar: {},
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
            colorPrimaryBg: '#543EDC',
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
            // Sort and hover feedback reads as a muddy grey wash by default. Tint
            // it with the brand purple so the affordance belongs to the palette.
            rowHoverBg: '#f4f0ff',
            headerSortActiveBg: '#f0ebff',
            headerSortHoverBg: '#e4dcff',
            bodySortBg: '#faf8ff',
        },
        Tooltip: {
            colorBgSpotlight: '#080635',
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
        colorPrimary: '#543EDC',
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
        ...borderTokens,
        ...textTokens,
        ...elevationTokens('8, 6, 53'),
    },
    cssVar: {},
};

const greenThemeConfig: ThemeConfig = {
    components: {
        Layout: {
            siderBg: '#2F4044',
            bodyBg: '#FFF',
            headerBg: token.colorBgContainer,
        },
        Button: {
            borderRadius: 10,
            colorPrimary: '#4D918B',
            primaryShadow: 'none',
        },
        Radio: {
            colorPrimary: '#4D918B',
        },
        Menu: {
            colorPrimaryBg: '#4D918B',
            darkItemBg: '#2F4044',
            itemBorderRadius: 10,
            darkPopupBg: '#2F4044',
            subMenuItemBorderRadius: 10,
            itemMarginInline: 5,
        },
        Table: {
            headerBorderRadius: 8,
            rowHoverBg: '#ebf4f1',
            headerSortActiveBg: '#e3efeb',
            headerSortHoverBg: '#d7e7e1',
            bodySortBg: '#f3f9f7',
        },
        Tooltip: {
            colorBgSpotlight: '#2F4044',
        },
        Tag: {
            colorInfo: '#E2D34E',
            colorInfoBg: 'rgba(226, 211, 78, 0.20)',
            colorInfoBorder: '#E2D34E',
            colorInfoText: '#744326',
            colorInfoTextActive: '#744326',
            colorSuccessText: '#265137',
            colorSuccess: '#265137',
        },
        Badge: {
            colorInfo: '#E6B14B',
            colorInfoBg: '#FCF0CC',
            colorInfoText: '#744326',
            colorInfoTextActive: '#744326',
        },
        Select: {
            optionSelectedBg: '#c9d6cf',
        },
        Input: {
            activeShadow: 'none',
        },
    },
    token: {
        // -------- Brand Colors ---------
        colorPrimary: '#3c9673',
        colorInfo: '#3c9673',
        colorInfoBg: '#ebf4f1',
        colorError: '#c73f1e',
        colorWarning: '#ffa62b',
        colorTextBase: '#463f3f',
        colorBgContainer: '#FFF',
        colorPrimaryBg: '#107072',
        // -------- Font ---------
        fontFamily: 'Neue Haas Grotesk Display Pro, sans-serif',
        fontWeightStrong: 600,
        // -------- Border ---------
        borderRadiusXS: 4,
        borderRadius: 10,
        borderRadiusLG: 16,
        // -------- Shadow ---------
        boxShadow: '0px 4px 9.2px 3px rgba(94, 94, 94, 0.09)',
        ...spacingTokens,
        ...borderTokens,
        ...textTokens,
        ...elevationTokens('47, 64, 68'),
    },
    algorithm: theme.defaultAlgorithm,
    cssVar: {},
};

export { blueThemeConfig, datamindedThemeConfig, greenThemeConfig };
