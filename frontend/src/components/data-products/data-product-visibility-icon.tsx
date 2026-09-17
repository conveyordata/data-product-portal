import { EyeInvisibleOutlined } from '@ant-design/icons';
import { Tag, Tooltip } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { DataProductVisibility } from '@/store/api/services/generated/dataProductsApi.ts';
import { getDataProductVisibilityLabel } from '@/utils/visibility-helper.ts';

type Props = {
    visibility: DataProductVisibility;
    iconOnly?: boolean;
};
export const DataProductVisibilityIcon = ({ visibility, iconOnly }: Props) => {
    const { t } = useTranslation();

    const icon = useMemo(() => {
        switch (visibility) {
            case DataProductVisibility.Discoverable:
                return null;
            case DataProductVisibility.Hidden:
                return <EyeInvisibleOutlined />;
            default:
                return null;
        }
    }, [visibility]);

    const tooltipTitle = () => {
        switch (visibility) {
            case DataProductVisibility.Discoverable:
                return undefined;
            case DataProductVisibility.Hidden:
                return t(
                    'This is a hidden Data Product, hidden Data Products are hidden from the rest of the organisation and use private Output Ports only.',
                );
            default:
                return undefined;
        }
    };

    return (
        <Tooltip title={tooltipTitle()}>
            {iconOnly ? icon : <Tag icon={icon}>{getDataProductVisibilityLabel(t, visibility)}</Tag>}
        </Tooltip>
    );
};
