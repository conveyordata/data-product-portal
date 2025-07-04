import type { ButtonProps, TooltipProps } from 'antd';
import { Button, ConfigProvider, Tooltip, theme } from 'antd';
import type { ReactNode } from 'react';

import styles from './circle-icon-button.module.scss';

const { useToken } = theme;

interface CircleIconButtonProps {
    icon: ReactNode;
    tooltip?: ReactNode;
    tooltipOptions?: Omit<TooltipProps, 'title'>;
    buttonProps?: Omit<ButtonProps, 'icon'>;
    onClick?: () => void;
}

export const CircleIconButton = ({ tooltip, tooltipOptions, buttonProps, icon, onClick }: CircleIconButtonProps) => {
    const { token } = useToken();
    const button = (
        <Button shape={'circle'} className={styles.circleIconButton} icon={icon} onClick={onClick} {...buttonProps} />
    );

    return tooltip ? (
        <ConfigProvider
            theme={{
                components: {
                    Button: {
                        defaultBorderColor: token.colorBorder,
                        defaultColor: token.colorText,
                    },
                },
            }}
        >
            <Tooltip title={tooltip} className={styles.tooltip} {...tooltipOptions}>
                {button}
            </Tooltip>
        </ConfigProvider>
    ) : (
        button
    );
};
