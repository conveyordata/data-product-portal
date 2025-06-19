import { CalendarOutlined, MailOutlined, PhoneOutlined, PushpinOutlined } from '@ant-design/icons';
import { Calendar, Card, Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import type { TagModel } from '@/types/tag';
import type { UserResponseContract } from '@/types/users/user.contract';
import styles from './user-description.module.scss';

type Props = {
    user: UserResponseContract;
};

export function UserDescription({ user }: Props) {
    const { t } = useTranslation();

    return (
        <Flex vertical className={styles.statusInfo}>
            <Space className={styles.contentSubtitle}>
                <Flex className={styles.statusBadge}>
                    <MailOutlined />
                    <Typography.Text strong>{user.email}</Typography.Text>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <CalendarOutlined />
                    <Typography.Text strong>
                        {t('Joined on ')}
                        {new Date(user.created_on).toLocaleDateString()}
                    </Typography.Text>
                    {/* <Typography.Text>{namespace}</Typography.Text> */}
                </Flex>
                {user.phone && (
                    <Flex className={styles.statusBadge}>
                        <PhoneOutlined />
                        <Typography.Text strong>{user.phone}</Typography.Text>
                        {/* <Typography.Text>{domain}</Typography.Text> */}
                    </Flex>
                )}
                {user.location && (
                    <Flex className={styles.statusBadge}>
                        <PushpinOutlined />
                        <Typography.Text strong>{user.location}</Typography.Text>
                        {/* <Typography.Text>{accessType}</Typography.Text> */}
                    </Flex>
                )}
            </Space>
            {user.bio && (
                <Space>
                    <Typography.Text italic>{user.bio}</Typography.Text>
                </Space>
            )}
        </Flex>
    );
}
