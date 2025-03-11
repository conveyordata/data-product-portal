import { EyeInvisibleOutlined } from '@ant-design/icons';
import { Popover } from 'antd';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import shieldHalfIcon from '@/assets/icons/shield-half-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { DatasetAccess } from '@/types/dataset';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper';

import styles from './dataset-access-icon.module.scss';

type Props = {
    accessType: DatasetAccess;
    hasPopover?: boolean;
};

export const DatasetAccessIcon = ({ accessType, hasPopover = false }: Props) => {
    const { t } = useTranslation();

    if (accessType === DatasetAccess.Public) {
        return null;
    }

    const icon =
        accessType === DatasetAccess.Restricted ? (
            <CustomSvgIconLoader iconComponent={shieldHalfIcon} size="x-small" color={'dark'} />
        ) : (
            <EyeInvisibleOutlined className={clsx(styles.defaultIcon, styles.dark, styles.xSmall)} />
        );

    return hasPopover ? (
        <Popover content={t('{{Type}} access', { Type: getDatasetAccessTypeLabel(t, accessType) })} placement={'top'}>
            {icon}
        </Popover>
    ) : (
        icon
    );
};
