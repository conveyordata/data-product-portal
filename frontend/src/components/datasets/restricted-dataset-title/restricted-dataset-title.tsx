import { Flex, Popover, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import shieldHalfIcon from '@/assets/icons/shield-half-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import styles from './restricted-dataset-title.module.scss';

type Props = {
    name: string;
    hasIcon?: boolean;
    hasPopover?: boolean;
};

export function RestrictedDatasetTitle({ name, hasIcon = true, hasPopover = false }: Props) {
    const { t } = useTranslation();

    const title = (
        <Flex className={styles.datasetTitle}>
            <Typography.Text strong>{name}</Typography.Text>
            {hasIcon && <CustomSvgIconLoader iconComponent={shieldHalfIcon} size="x-small" color={'dark'} />}
        </Flex>
    );

    return hasPopover ? (
        <Popover content={t('Restricted access')} trigger="hover">
            {title}
        </Popover>
    ) : (
        title
    );
}
