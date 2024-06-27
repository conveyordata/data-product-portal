import { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Flex } from 'antd';
import styles from './breadcrumb-link.module.scss';
import clsx from 'clsx';

type BreadcrumbLinkProps = {
    title: ReactNode;
    isActive?: boolean;
    to?: string;
    icon?: ReactNode;
    separator?: ReactNode;
};

const fallbackTo = '#';

export const BreadcrumbLink = ({ to = fallbackTo, isActive = false, icon, title, separator }: BreadcrumbLinkProps) => {
    const breadcrumbItem = (
        <Flex className={clsx(styles.breadcrumbWrapper, { [styles.current]: isActive })}>
            {icon}
            {title}
        </Flex>
    );

    if (isActive) {
        return breadcrumbItem;
    }

    return (
        <Flex className={styles.linkContainer}>
            <Link className={styles.link} to={to}>
                {breadcrumbItem}
            </Link>
            {separator}
        </Flex>
    );
};
