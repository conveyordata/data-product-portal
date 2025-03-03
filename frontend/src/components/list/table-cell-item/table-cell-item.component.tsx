import Icon from '@ant-design/icons';
import { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';
import { Flex, Popover, Typography, TypographyProps } from 'antd';
import type { TooltipPlacement } from 'antd/es/tooltip';
import * as React from 'react';
import { ComponentType, ReactNode } from 'react';

import styles from './table-cell-item.module.scss';

type Props = {
    icon?: ReactNode;
    reactSVGComponent?:
        | ComponentType<CustomIconComponentProps | React.SVGProps<SVGSVGElement>>
        | React.ForwardRefExoticComponent<CustomIconComponentProps>;
    children?: ReactNode;
    text?: string;
    textComponent?: ReactNode;
    textProps?: TypographyProps['Text'];
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
    const [hasEllipsis, setHasEllipsis] = React.useState<boolean>(false);

    const tableCellItem = (
        <Flex className={styles.tableCellWrapper} {...otherProps}>
            {icon && icon}
            {reactSVGComponent && <Icon component={reactSVGComponent} className={styles.customIcon} />}
            {text && (
                <Typography.Text
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
                </Typography.Text>
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
