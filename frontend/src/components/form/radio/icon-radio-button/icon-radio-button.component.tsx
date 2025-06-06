import { Flex, type FlexProps, Radio, type RadioProps, Typography } from 'antd';
import type { ReactNode } from 'react';

import styles from './icon-radio-button.module.scss';

type CustomRadioButtonProps = RadioProps & {
    icon: ReactNode;
    label?: string;
    containerProps?: FlexProps;
    isDisabled?: boolean;
};
export const IconRadioButton = ({ icon, label, containerProps, isDisabled, ...props }: CustomRadioButtonProps) => {
    return (
        <Flex vertical className={styles.radioButtonContainer} {...containerProps}>
            <Radio.Button disabled={isDisabled} rootClassName={styles.radioButton} {...props}>
                <Flex vertical className={styles.iconWrapper}>
                    {icon}
                </Flex>
            </Radio.Button>
            {label && <Typography.Text>{label}</Typography.Text>}
        </Flex>
    );
};
