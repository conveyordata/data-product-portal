import { EyeInvisibleOutlined } from '@ant-design/icons';
import { Tag, Tooltip } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import shieldHalfIcon from '@/assets/icons/shield-half-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { OutputPortAccessType } from '@/store/api/services/generated/dataProductsApi.ts';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper.ts';

type Props = {
    accessType: OutputPortAccessType;
    iconOnly?: boolean;
};

export const OutputPortAccessIcon = ({ accessType, iconOnly }: Props) => {
    const { t } = useTranslation();

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
                    'This is a restricted Output Port, to gain access users can request access through the Marketplace, and access requests will be approved by the owner',
                );
            case OutputPortAccessType.Private:
                return t(
                    'This is a private Output Port, private Output Ports are hidden from the rest of the organisation and can only be accessed by users with access to the Output Port. The owner has the ability to add consumers directly',
                );
            default:
                return undefined;
        }
    };

    return (
        <Tooltip title={tooltipTitle()}>
            {iconOnly ? icon : <Tag icon={icon}>{getDatasetAccessTypeLabel(t, accessType)}</Tag>}
        </Tooltip>
    );
};
