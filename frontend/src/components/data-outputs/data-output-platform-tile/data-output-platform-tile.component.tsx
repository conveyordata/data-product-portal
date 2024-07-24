import { Environment } from '@/types/environment';
import { Dropdown, DropdownProps, Flex, MenuProps, Radio, Space, Spin, Typography } from 'antd';
import styles from './data-output-platform-tile.module.scss';
import { CustomDropdownItemProps } from '@/types/shared';
import { useTranslation } from 'react-i18next';
import { useMemo } from 'react';
import Icon from '@ant-design/icons';

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
    environments,
    isLoading,
    isDisabled,
    isSelected,
    onMenuItemClick = () => {},
    onTileClick = () => {},
}: Props<T>) {
    const { t } = useTranslation();
    const isDisabledDropdown = isDisabled || dataPlatform.disabled;
    const isMenuDisabled = dataPlatform.hasMenu;

    const items: MenuProps['items'] = useMemo(
        () => [
            {
                type: 'group',
                // children: environments?.map((env) => ({
                //     key: env.name,
                //     label: env.name,
                //     disabled: isDisabled,
                //     onClick: ({ key }) => onMenuItemClick(key, dataPlatform.value),
                // })),
            },
        ],
        [environments, isDisabled, onMenuItemClick, dataPlatform.value, t],
    );

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
