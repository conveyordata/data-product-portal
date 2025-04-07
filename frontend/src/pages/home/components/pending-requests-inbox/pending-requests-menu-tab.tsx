import { Badge, Col, Flex, Tag, Typography } from 'antd';
import { useState } from 'react';

import styles from '@/pages/home/components/pending-requests-inbox/pending-requests-inbox.module.scss';
import { NotificationTypes } from '@/types/notifications/notification.contract';

interface SelectableTabProps {
    type: NotificationTypes;
    title: string;
    requestsCount: number;
    color: string;
    onSelectChange?: (type: NotificationTypes, selected: boolean) => void;
}

export const SelectableTab = ({ type, title, requestsCount, color, onSelectChange }: SelectableTabProps) => {
    const [selected, setSelected] = useState(false);

    return (
        <Col>
            <Tag.CheckableTag
                style={{
                    borderBottom: selected ? `5px solid ${color}` : '5px solid transparent',
                }}
                className={`${styles.menuItem} ${selected ? styles.menuItemActive : ''}`}
                checked={selected}
                onChange={(checked) => {
                    setSelected(checked);
                    onSelectChange?.(type, checked);
                }}
            >
                <Flex vertical>
                    <Typography.Text>
                        <div>
                            {title}
                            <Badge count={requestsCount} color="gray" size="small" className={styles.tabItemsCount} />
                        </div>
                    </Typography.Text>
                </Flex>
            </Tag.CheckableTag>
        </Col>
    );
};
