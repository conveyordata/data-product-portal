import { Flex, Popover, PopoverProps, Space, Typography } from 'antd';
import styles from './table-cell-avatar.module.scss';
import { ReactNode } from 'react';
import { Link } from 'react-router-dom';

type Props = {
    title: ReactNode | string;
    subtitle: ReactNode | string;
    icon: ReactNode;
    popover?: PopoverProps;
    linkTo?: string;
};

const PopoverComponent = (props: PopoverProps) => (
    <Popover {...props}>
        <div>{props.children}</div>
    </Popover>
);

const LinkElement = ({ to, children }: { to: string; children: ReactNode }) => <Link to={to}>{children}</Link>;

export const TableCellAvatar = ({ title, subtitle, icon, popover, linkTo }: Props) => {
    const baseComponent = (
        <Space className={styles.avatarContainer}>
            <Flex className={styles.avatarContainer}>
                {icon}
                <Flex vertical>
                    {typeof title === 'string' ? <Typography.Text strong>{title}</Typography.Text> : title}
                    {typeof subtitle === 'string' ? <Typography.Text>{subtitle}</Typography.Text> : subtitle}
                </Flex>
            </Flex>
        </Space>
    );
    let component = baseComponent;

    if (linkTo) {
        component = <LinkElement to={linkTo}>{baseComponent}</LinkElement>;
    }

    if (popover) {
        component = (
            <PopoverComponent placement={'topLeft'} overlayClassName={styles.popoverContent} {...popover}>
                {component}
            </PopoverComponent>
        );
    }

    return component;
};
