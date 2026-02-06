import { EyeInvisibleOutlined } from '@ant-design/icons';
import { Popover } from 'antd';
import clsx from 'clsx';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import shieldHalfIcon from '@/assets/icons/shield-half-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { OutputPortAccessType } from '@/store/api/services/generated/dataProductsApi.ts';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper';
import styles from './output-port-access-icon.module.scss';

type Props = {
    accessType: OutputPortAccessType;
    hasPopover?: boolean;
};

export const OutputPortAccessIcon = ({ accessType, hasPopover = false }: Props) => {
    const { t } = useTranslation();

    const icon = useMemo(() => {
        switch (accessType) {
            case OutputPortAccessType.Public:
                return null;
            case OutputPortAccessType.Restricted:
                return <CustomSvgIconLoader iconComponent={shieldHalfIcon} size="x-small" color={'dark'} />;
            case OutputPortAccessType.Private:
                return <EyeInvisibleOutlined className={clsx(styles.defaultIcon, styles.dark, styles.xSmall)} />;
            default:
                return null;
        }
    }, [accessType]);

    return hasPopover ? (
        <Popover content={t('{{Type}} access', { Type: getDatasetAccessTypeLabel(t, accessType) })} placement={'top'}>
            {icon}
        </Popover>
    ) : (
        icon
    );
};
