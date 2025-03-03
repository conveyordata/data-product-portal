import { theme,ThemeConfig } from 'antd';

const { getDesignToken } = theme;

const token = getDesignToken();

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
    },
    token: {
        fontFamily: 'SF Pro Text, sans-serif',
        fontSize: 14,
        fontSizeHeading1: 38,
        fontSizeHeading2: 30,
        fontSizeHeading3: 24,
        fontSizeHeading4: 20,
        fontSizeHeading5: 16,
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
        // Error
        colorError: '#FF4D4F',
        colorErrorBg: '#FFF2F0',
        colorErrorBgHover: '#FFF1F0',
        colorErrorBorder: '#FFCCC7',
        colorErrorBorderHover: '#FFA39E',
        colorErrorHover: '#FF7875',
        colorErrorActive: '#D9363E',
        colorErrorText: '#FF4D4F',
        colorErrorTextHover: '#FF7875',
        colorErrorTextActive: '#D9363E',
        colorErrorOutline: '#FF2696',
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
    },
    cssVar: true,
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
        colorError: '#c73f1e',
        colorWarning: '#ffa62b',
        colorTextBase: '#463f3f',
        colorBgContainer: '#FFF',
        colorPrimaryBg: '#107072',
        // -------- Font ---------
        fontFamily: 'Neue Haas Grotesk Display Pro, sans-serif',
        fontSize: 16,
        fontSizeHeading1: 38,
        fontSizeHeading2: 32,
        fontSizeHeading3: 24,
        fontSizeHeading4: 20,
        fontSizeHeading5: 16,
        fontWeightStrong: 600,
        // -------- Border ---------
        borderRadiusXS: 4,
        borderRadius: 10,
        borderRadiusLG: 16,
        colorBorder: '#E7E7E7',
        // -------- Shadow ---------
        boxShadow: '0px 4px 9.2px 3px rgba(94, 94, 94, 0.09)',
        boxShadowSecondary: '2px 7px 9px 0px rgba(116, 111, 111, 0.15)',
        // -------- Spacing ---------
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
    },
    algorithm: theme.defaultAlgorithm,
    cssVar: true,
};

export { blueThemeConfig, greenThemeConfig };
