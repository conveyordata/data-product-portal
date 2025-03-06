import { List, Typography } from 'antd';
import { ReactNode } from 'react';
import { Link } from 'react-router';

import styles from './usage-list-item.module.scss';

type Props = {
    itemId: string;
    title: string;
    description: string;
    icon: ReactNode;
    linkTo?: string;
};

export function UsageListItem({ itemId, title, description, icon, linkTo }: Props) {
    return (
        <List.Item key={itemId} className={styles.listItem}>
            <Link to={linkTo ?? ''}>
                <List.Item.Meta
                    className={styles.itemCard}
                    avatar={icon}
                    title={<Typography.Text className={styles.userName}>{title}</Typography.Text>}
                    description={<Typography.Text>{description}</Typography.Text>}
                />
            </Link>
        </List.Item>
    );
}
