import Icon from '@ant-design/icons';
import type { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';
import { Flex, Tooltip, Typography, type TypographyProps } from 'antd';
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
    const [isTruncated, setIsTruncated] = useState(false);

    return (
        <Flex className={styles.tableCellWrapper} {...otherProps}>
            {icon}
            {reactSVGComponent && <Icon component={reactSVGComponent} className={styles.customIcon} />}
            {text && (
                <Tooltip title={isTruncated && tooltip?.content} placement={tooltip?.placement ?? 'topLeft'}>
                    <Text
                        {...textProps}
                        ellipsis
                        className={styles.text}
                        onMouseEnter={(e) => setIsTruncated(e.currentTarget.scrollWidth > e.currentTarget.clientWidth)}
                    >
                        {text}
                    </Text>
                </Tooltip>
            )}
            {textComponent && textComponent}
            {children}
        </Flex>
    );
}
