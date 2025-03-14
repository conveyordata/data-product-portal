import { Flex, Popover, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

import { DatasetAccess } from '@/types/dataset';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper';

import { DatasetAccessIcon } from '../dataset-access-icon/dataset-access-icon';
import styles from './dataset-title.module.scss';

type Props = {
    name: string;
    accessType: DatasetAccess;
    hasIcon?: boolean;
    hasPopover?: boolean;
};

export function DatasetTitle({ name, accessType, hasIcon = true, hasPopover = false }: Props) {
    const { t } = useTranslation();

    const title = (
        <Flex className={styles.datasetTitle}>
            <Typography.Text strong>{name}</Typography.Text>
            {accessType !== DatasetAccess.Public && hasIcon && <DatasetAccessIcon accessType={accessType} />}
        </Flex>
    );

    if (accessType === DatasetAccess.Public) {
        return title;
    }

    return hasPopover ? (
        <Popover content={t('{{Type}} access', { Type: getDatasetAccessTypeLabel(t, accessType) })} trigger="hover">
            {title}
        </Popover>
    ) : (
        title
    );
}
