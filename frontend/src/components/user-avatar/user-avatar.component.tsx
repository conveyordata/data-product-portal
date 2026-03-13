import { UserOutlined } from '@ant-design/icons';
import { Avatar } from 'antd';
import type { UserContract } from '@/types/users';
import styles from './user-avatar.module.scss';

type Props = {
    user?: UserContract;
    color?: string;
    size?: 'small' | 'default' | 'large';
};

export function UserAvatar({ user, color, size = 'default' }: Props) {
    const userInitials = user?.first_name?.charAt(0) + (user?.last_name ? user.last_name.charAt(0) : '');
    return (
        <Avatar size={size} className={styles.avatar} style={{ backgroundColor: color }}>
            {userInitials || <UserOutlined />}
        </Avatar>
    );
}
