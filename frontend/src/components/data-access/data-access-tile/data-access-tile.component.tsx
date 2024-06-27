import { Environment } from '@/types/environment';
import { Dropdown, DropdownProps, Flex, MenuProps, Radio, Space, Spin, Typography } from 'antd';
import styles from './data-access-tile.module.scss';
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
};

const ACCESS_DATA_DROPDOWN_DELAY = 0.25;

export function AccessDataTile<T extends string>({
    dataPlatform,
    environments,
    isLoading,
    isDisabled,
    onMenuItemClick = () => {},
    dropdownProps,
    onTileClick = () => {},
}: Props<T>) {
    const { t } = useTranslation();
    const isDisabledDropdown = isDisabled || dataPlatform.disabled;
    const isMenuDisabled = dataPlatform.hasMenu;

    const items: MenuProps['items'] = useMemo(
        () => [
            {
                type: 'group',
                label: t('Environments'),
                children: environments?.map((env) => ({
                    key: env.name,
                    label: env.name,
                    disabled: isDisabled,
                    onClick: ({ key }) => onMenuItemClick(key, dataPlatform.value),
                })),
            },
        ],
        [environments, isDisabled, onMenuItemClick, dataPlatform.value, t],
    );

    return (
        <Flex vertical className={styles.radioButtonContainer}>
            <div>
                <Dropdown
                    placement={'bottom'}
                    menu={{
                        items,
                    }}
                    mouseLeaveDelay={ACCESS_DATA_DROPDOWN_DELAY}
                    disabled={isDisabledDropdown || !isMenuDisabled}
                    trigger={['hover']}
                    arrow
                    {...dropdownProps}
                >
                    <Space>
                        <Radio.Button
                            rootClassName={styles.radioButton}
                            disabled={isDisabledDropdown}
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
                </Dropdown>
            </div>
            <Typography.Text className={styles.label} ellipsis>
                {dataPlatform.label}
            </Typography.Text>
        </Flex>
    );
}
