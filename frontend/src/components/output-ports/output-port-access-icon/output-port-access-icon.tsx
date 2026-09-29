import { Tag, Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';
import type { OutputPortClassification } from '@/store/api/services/generated/dataProductsApi.ts';
import { getAccessFunctionInfo } from '@/utils/access-function.helper.tsx';

type Props = {
    classification: OutputPortClassification;
    iconOnly?: boolean;
};

export const OutputPortAccessIcon = ({ classification, iconOnly }: Props) => {
    const { t } = useTranslation();
    const { icon, tooltip } = getAccessFunctionInfo(t, classification.access_function);

    return <Tooltip title={tooltip}>{iconOnly ? icon : <Tag icon={icon}>{classification.name}</Tag>}</Tooltip>;
};
