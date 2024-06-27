import styles from './table-cell-item.module.scss';
import { Flex, Popover, Typography, TypographyProps } from 'antd';
import * as React from 'react';
import { ComponentType, ReactNode } from 'react';
import Icon from '@ant-design/icons';
import { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';

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
    };
};

export function TableCellItem({ icon, text, textProps, textComponent, children, reactSVGComponent, tooltip }: Props) {
    const [hasEllipsis, setHasEllipsis] = React.useState<boolean>(false);

    const tableCellItem = (
        <Flex className={styles.tableCellWrapper}>
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
        <Popover placement={'topLeft'} {...tooltip}>
            {tableCellItem}
        </Popover>
    ) : (
        tableCellItem
    );
}
