import Icon from '@ant-design/icons';
import { Flex, Radio, Typography } from 'antd';

import type { CustomDropdownItemProps } from '@/types/shared';

import styles from './data-output-platform-tile.module.scss';

type Props<T extends string> = {
    dataPlatform: CustomDropdownItemProps<T>;
    onTileClick?: (dataPlatform: CustomDropdownItemProps<T>) => void;
    isDisabled?: boolean;
    isSelected?: boolean;
    value?: string;
};

export function DataOutputPlatformTile<T extends string>({
    dataPlatform,
    isDisabled,
    isSelected,
    onTileClick = (): void => undefined,
    value,
}: Props<T>) {
    const isDisabledDropdown = isDisabled || dataPlatform.disabled;

    return (
        <Flex vertical className={styles.radioButtonContainer} gap={'small'}>
            <Radio.Button
                rootClassName={styles.radioButton}
                disabled={isDisabledDropdown}
                checked={isSelected}
                onClick={() => onTileClick(dataPlatform)}
                value={value}
                aria-label={dataPlatform.label}
            >
                <Icon component={dataPlatform.icon} className={styles.icon} />
            </Radio.Button>
            <Typography.Text className={styles.label} ellipsis>
                {dataPlatform.label}
            </Typography.Text>
        </Flex>
    );
}
