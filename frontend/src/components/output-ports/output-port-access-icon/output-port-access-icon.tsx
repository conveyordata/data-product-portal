import { Tag, Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';
import type { OutputPortAccessType } from '@/store/api/services/generated/dataProductsApi.ts';
import { getAccessFunctionInfo } from '@/utils/access-function.helper.tsx';

type Props = {
    accessType: OutputPortAccessType;
    iconOnly?: boolean;
};

export const OutputPortAccessIcon = ({ accessType, iconOnly }: Props) => {
    const { t } = useTranslation();
    const { icon, tooltip } = getAccessFunctionInfo(t, accessType.access_function);

    return <Tooltip title={tooltip}>{iconOnly ? icon : <Tag icon={icon}>{accessType.name}</Tag>}</Tooltip>;
};
