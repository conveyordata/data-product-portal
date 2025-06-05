import Icon from '@ant-design/icons';
import type { CustomIconComponentProps } from '@ant-design/icons/lib/components/Icon';
import clsx from 'clsx';
import type { ComponentType, ForwardRefExoticComponent, SVGProps } from 'react';

import styles from './custom-svg-icon-loader.module.scss';

type Props = {
    iconComponent:
        | ComponentType<CustomIconComponentProps | SVGProps<SVGSVGElement>>
        | ForwardRefExoticComponent<CustomIconComponentProps>
        | undefined;
    size?: 'x-small' | 'small' | 'default' | 'large' | 'x-large';
    hasRoundBorder?: boolean;
    hasSquareBorder?: boolean;
    color?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'light' | 'dark';
    inverted?: boolean;
};
export const CustomSvgIconLoader = ({
    iconComponent,
    hasRoundBorder = false,
    hasSquareBorder = false,
    size = 'default',
    color = 'primary',
    inverted = false,
    ...otherProps
}: Props) => {
    return (
        <Icon
            component={iconComponent}
            className={clsx([styles.defaultIcon, { [styles.iconBorder]: hasRoundBorder }, styles[size]], {
                [styles[color]]: color,
                [styles.inverted]: inverted,
                [styles.squareBorder]: hasSquareBorder,
            })}
            {...otherProps}
        />
    );
};
