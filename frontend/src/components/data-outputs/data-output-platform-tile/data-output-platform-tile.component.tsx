import Icon from '@ant-design/icons';
import { DropdownProps, Flex, Radio, Space, Spin, Typography } from 'antd';

import { Environment } from '@/types/environment';
import { CustomDropdownItemProps } from '@/types/shared';

import styles from './data-output-platform-tile.module.scss';

type Props<T extends string> = {
    dataPlatform: CustomDropdownItemProps<T>;
    environments: Environment[];
    onMenuItemClick?: (environment: string, dataPlatform: T) => void;
    onTileClick?: (dataPlatform: T) => void;
    dropdownProps?: DropdownProps;
    isLoading?: boolean;
    isDisabled?: boolean;
    isSelected?: boolean;
};

export function DataOutputPlatformTile<T extends string>({
    dataPlatform,
    isLoading,
    isDisabled,
    isSelected,
    onTileClick = () => {},
}: Props<T>) {
    const isDisabledDropdown = isDisabled || dataPlatform.disabled;

    return (
        <Flex vertical className={styles.radioButtonContainer}>
            <div>
                <Space>
                    <Radio.Button
                        rootClassName={styles.radioButton}
                        disabled={isDisabledDropdown}
                        checked={isSelected}
                        onClick={() => onTileClick(dataPlatform.value)}
                    >
                        <Flex vertical className={styles.iconWrapper}>
                            {isLoading ? (
                                <Spin size={'small'}>
                                    <Icon component={dataPlatform.icon} className={styles.icon} />
                                </Spin>
                            ) : (
                                <Icon component={dataPlatform.icon} className={styles.icon} />
                            )}
                        </Flex>
                    </Radio.Button>
                </Space>
            </div>
            <Typography.Text className={styles.label} ellipsis>
                {dataPlatform.label}
            </Typography.Text>
        </Flex>
    );
}
