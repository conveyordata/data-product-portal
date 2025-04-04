import { Tag, Col, Typography, Space, Flex, Badge } from 'antd';
import { useState } from 'react';
import styles from '@/pages/home/components/pending-requests-inbox/pending-requests-inbox.module.scss';

interface SelectableTabProps {
    title: string;
    requestsCount: number;
    color: string;
    defaultSelected?: boolean;
}

export const SelectableTab = ({ title, requestsCount, color, defaultSelected = false }: SelectableTabProps) => {
    const [selected, setSelected] = useState(defaultSelected);

    return (
        <Col>
            <Tag.CheckableTag
                style={{
                    borderBottom: selected ? `5px solid ${color}` : '5px solid transparent',
                }}
                className={`${styles.menuItem} ${selected ? styles.menuItemActive : ''}`}
                checked={selected}
                onChange={(checked) => setSelected(checked)}
            >
                <Flex vertical>
                    <Typography.Text strong style={{ whiteSpace: 'nowrap' }}>
                        {title} <Badge count={requestsCount} color="gray" size="small" />
                    </Typography.Text>
                </Flex>
            </Tag.CheckableTag>
        </Col>
    );
};
