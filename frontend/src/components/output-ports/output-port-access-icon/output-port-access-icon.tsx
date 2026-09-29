import { EyeInvisibleOutlined } from '@ant-design/icons';
import { Tag, Tooltip } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import shieldHalfIcon from '@/assets/icons/shield-half-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import {
    OutputPortAccessFunction,
    type OutputPortClassification,
} from '@/store/api/services/generated/dataProductsApi.ts';

type Props = {
    classification: OutputPortClassification;
    iconOnly?: boolean;
};

export const OutputPortAccessIcon = ({ classification, iconOnly }: Props) => {
    const { t } = useTranslation();
    const accessFunction = classification.access_function;

    const icon = useMemo(() => {
        switch (accessFunction) {
            case OutputPortAccessFunction.Unrestricted:
                return null;
            case OutputPortAccessFunction.Restricted:
                return <CustomSvgIconLoader iconComponent={shieldHalfIcon} size="font-small" color="dark" />;
            case OutputPortAccessFunction.Private:
                return <EyeInvisibleOutlined />;
            default:
                return null;
        }
    }, [accessFunction]);

    const tooltipTitle = () => {
        switch (accessFunction) {
            case OutputPortAccessFunction.Unrestricted:
                return undefined;
            case OutputPortAccessFunction.Restricted:
                return t(
                    'To gain access to this Output Port, users request access through the Marketplace, and the owner approves the requests',
                );
            case OutputPortAccessFunction.Private:
                return t(
                    'This Output Port is hidden from the rest of the organisation and can only be accessed by users with access to it. The owner can add consumers directly',
                );
            default:
                return undefined;
        }
    };

    return <Tooltip title={tooltipTitle()}>{iconOnly ? icon : <Tag icon={icon}>{classification.name}</Tag>}</Tooltip>;
};
