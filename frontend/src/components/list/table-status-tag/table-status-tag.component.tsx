import { Status } from '@/types/shared';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper.ts';
import { Badge, Tag } from 'antd';
import styles from './table-status-tag.module.scss';

export function TableStatusTag({ status }: { status: Status }) {
    return (
        <Tag color={getBadgeStatus(status)} className={styles.tag}>
            <Badge status={getBadgeStatus(status)} text={getStatusLabel(status)} />
        </Tag>
    );
}
