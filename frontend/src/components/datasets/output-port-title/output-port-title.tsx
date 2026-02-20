import { Flex, Popover, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { OutputPortAccessType } from '@/store/api/services/generated/dataProductsApi.ts';
import { getDatasetAccessTypeLabel } from '@/utils/access-type.helper';
import { OutputPortAccessIcon } from '../output-port-access-icon/output-port-access-icon.tsx';
import styles from './dataset-title.module.scss';

type Props = {
    name: string;
    accessType: OutputPortAccessType;
    hasIcon?: boolean;
    hasPopover?: boolean;
};

export function OutputPortTitle({ name, accessType, hasIcon = true, hasPopover = false }: Props) {
    const { t } = useTranslation();

    const title = (
        <Flex className={styles.datasetTitle}>
            <Typography.Text strong>{name}</Typography.Text>
            {accessType !== OutputPortAccessType.Public && hasIcon && <OutputPortAccessIcon accessType={accessType} />}
        </Flex>
    );

    if (accessType === OutputPortAccessType.Public) {
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
