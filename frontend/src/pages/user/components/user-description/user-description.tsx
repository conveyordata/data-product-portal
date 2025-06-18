import { CalendarOutlined, MailOutlined, PhoneOutlined, PushpinOutlined } from '@ant-design/icons';
import { Card, Flex, Space, Tag, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import type { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import type { TagModel } from '@/types/tag';
import type { UserResponseContract } from '@/types/users/user.contract';
import styles from './dataset-description.module.scss';

type Props = {
    user: UserResponseContract;
};

export function UserDescription({ user }: Props) {
    const { t } = useTranslation();

    return (
        <Card className="mb-6">
            <CardContent className="p-6">
                <div className="flex items-start space-x-6">
                    {/* <div className={`w-20 h-20 rounded-full flex items-center justify-center text-2xl font-medium ${getAvatarColor(user.name)}`}>
          {initials}
        </div> */}

                    <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                            <h2 className="text-2xl font-bold text-gray-900">
                                {user.first_name} {user.last_name}
                            </h2>
                            {/* {getStatusBadge(user.status)} */}
                            {/* {getRoleBadge(user.role)} */}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
                            <div className="flex items-center space-x-2 text-gray-600">
                                <MailOutlined className="w-4 h-4" />
                                <span className="text-sm">{user.email}</span>
                            </div>
                            {user.phone && (
                                <div className="flex items-center space-x-2 text-gray-600">
                                    <PhoneOutlined className="w-4 h-4" />
                                    <span className="text-sm">{user.phone}</span>
                                </div>
                            )}
                            {user.location && (
                                <div className="flex items-center space-x-2 text-gray-600">
                                    <PushpinOutlined className="w-4 h-4" />
                                    <span className="text-sm">{user.location}</span>
                                </div>
                            )}
                            <div className="flex items-center space-x-2 text-gray-600">
                                <CalendarOutlined className="w-4 h-4" />
                                <span className="text-sm">Joined {new Date(user.joinDate).toLocaleDateString()}</span>
                            </div>
                        </div>
                    </div>

                    {/* <div className="text-right">
          <div className="text-2xl font-bold text-gray-900">{user.dataProducts}</div>
          <div className="text-sm text-gray-500">Data Products</div>
        </div> */}
                </div>
            </CardContent>
        </Card>
        /* </Card>

    return (
        <Flex vertical className={styles.statusInfo}>
            <Space className={styles.contentSubtitle}>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Status')}</Typography.Text>
                    <Tag color={lifecycle.color}>{lifecycle.name}</Tag>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Namespace')}</Typography.Text>
                    <Typography.Text>{namespace}</Typography.Text>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Domain')}</Typography.Text>
                    <Typography.Text>{domain}</Typography.Text>
                </Flex>
                <Flex className={styles.statusBadge}>
                    <Typography.Text strong>{t('Access Type')}</Typography.Text>
                    <Typography.Text>{accessType}</Typography.Text>
                </Flex>
            </Space>
            <Flex>
                {tags.map((tag) => (
                    <Tag color={tag.rolled_up ? 'red' : 'success'} key={tag.id}>
                        {tag.value}
                    </Tag>
                ))}
            </Flex>
            <Space>
                <Typography.Text italic>{description}</Typography.Text>
            </Space>
        </Flex> */
    );
}
