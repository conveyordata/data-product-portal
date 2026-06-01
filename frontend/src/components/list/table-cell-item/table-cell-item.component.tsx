import Icon from '@ant-design/icons';
import type { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';
import { Flex, Popover, Typography, type TypographyProps } from 'antd';
import type { TooltipPlacement } from 'antd/es/tooltip';
import { type ComponentType, type ForwardRefExoticComponent, type ReactNode, type SVGProps, useState } from 'react';
import styles from './table-cell-item.module.scss';

const { Text } = Typography;

type Props = {
    icon?: ReactNode;
    reactSVGComponent?:
        | ComponentType<CustomIconComponentProps | SVGProps<SVGSVGElement>>
        | ForwardRefExoticComponent<CustomIconComponentProps>;
    children?: ReactNode;
    text?: string;
    textComponent?: ReactNode;
    textProps?: TypographyProps;
    tooltip?: {
        title?: ReactNode;
        content?: ReactNode;
        placement?: TooltipPlacement;
    };
};

export function TableCellItem({
    icon,
    text,
    textProps,
    textComponent,
    children,
    reactSVGComponent,
    tooltip,
    ...otherProps
}: Props) {
    const [hasEllipsis, setHasEllipsis] = useState<boolean>(false);

    const tableCellItem = (
        <Flex className={styles.tableCellWrapper} {...otherProps}>
            {icon}
            {reactSVGComponent && <Icon component={reactSVGComponent} className={styles.customIcon} />}
            {text && (
                <Text
                    {...textProps}
                    ellipsis={{
                        onEllipsis: () => {
                            if (tooltip) {
                                setHasEllipsis(true);
                            }
                        },
                    }}
                    className={styles.text}
                >
                    {text}
                </Text>
            )}
            {textComponent && textComponent}
            {children}
        </Flex>
    );

    return hasEllipsis ? (
        <Popover placement={tooltip?.placement || 'topLeft'} {...tooltip}>
            {tableCellItem}
        </Popover>
    ) : (
        tableCellItem
    );
}
