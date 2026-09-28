import { EyeInvisibleOutlined } from '@ant-design/icons';
import { Tag, Tooltip } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import shieldHalfIcon from '@/assets/icons/shield-half-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { OutputPortAccessType, type OutputPortClassification } from '@/store/api/services/generated/dataProductsApi.ts';

type Props = {
    classification: OutputPortClassification;
    iconOnly?: boolean;
};

export const OutputPortAccessIcon = ({ classification, iconOnly }: Props) => {
    const { t } = useTranslation();
    const accessType = classification.access_type;

    const icon = useMemo(() => {
        switch (accessType) {
            case OutputPortAccessType.Unrestricted:
                return null;
            case OutputPortAccessType.Restricted:
                return <CustomSvgIconLoader iconComponent={shieldHalfIcon} size="font-small" color="dark" />;
            case OutputPortAccessType.Private:
                return <EyeInvisibleOutlined />;
            default:
                return null;
        }
    }, [accessType]);

    const tooltipTitle = () => {
        switch (accessType) {
            case OutputPortAccessType.Unrestricted:
                return undefined;
            case OutputPortAccessType.Restricted:
                return t(
                    'To gain access to this Output Port, users request access through the Marketplace, and the owner approves the requests',
                );
            case OutputPortAccessType.Private:
                return t(
                    'This Output Port is hidden from the rest of the organisation and can only be accessed by users with access to it. The owner can add consumers directly',
                );
            default:
                return undefined;
        }
    };

    return <Tooltip title={tooltipTitle()}>{iconOnly ? icon : <Tag icon={icon}>{classification.name}</Tag>}</Tooltip>;
};
