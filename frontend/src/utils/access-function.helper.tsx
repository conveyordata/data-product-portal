import { EyeInvisibleOutlined } from '@ant-design/icons';
import type { TFunction } from 'i18next';
import type { ReactNode } from 'react';
import shieldHalfIcon from '@/assets/icons/shield-half-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { OutputPortAccessFunction } from '@/store/api/services/generated/dataProductsApi.ts';

export const ACCESS_FUNCTION_ORDER = [
    OutputPortAccessFunction.Unrestricted,
    OutputPortAccessFunction.Restricted,
    OutputPortAccessFunction.Private,
];

export const compareAccessFunctions = (a: OutputPortAccessFunction, b: OutputPortAccessFunction) =>
    ACCESS_FUNCTION_ORDER.indexOf(a) - ACCESS_FUNCTION_ORDER.indexOf(b);

export const fitsDataProductVisibility = (accessFunction: OutputPortAccessFunction, hiddenDataProduct: boolean) =>
    !hiddenDataProduct || accessFunction === OutputPortAccessFunction.Private;

export const getAccessFunctionInfo = (
    t: TFunction,
    accessFunction: OutputPortAccessFunction,
): { label: string; icon: ReactNode; tooltip?: string } =>
    ({
        [OutputPortAccessFunction.Unrestricted]: { label: t('Auto-approve'), icon: null },
        [OutputPortAccessFunction.Restricted]: {
            label: t('Approval required'),
            icon: <CustomSvgIconLoader iconComponent={shieldHalfIcon} size="font-small" color="dark" />,
            tooltip: t(
                'To gain access to this Output Port, users request access through the Marketplace, and the owner approves the requests',
            ),
        },
        [OutputPortAccessFunction.Private]: {
            label: t('Invite only (hidden)'),
            icon: <EyeInvisibleOutlined />,
            tooltip: t(
                'This Output Port is hidden from the rest of the organisation and can only be accessed by users with access to it. The owner can add consumers directly',
            ),
        },
    })[accessFunction];

export const getAccessFunctionLabel = (t: TFunction, accessFunction: OutputPortAccessFunction) =>
    getAccessFunctionInfo(t, accessFunction).label;
