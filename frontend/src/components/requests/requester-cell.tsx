import { Space, theme } from 'antd';
import type { UserContract } from '@/types/users';
import { UserAvatarWithEmail } from '../user-avatar/user-avatar-with-email.component';

type Props = {
    user: UserContract;
};

export function RequesterCell({ user }: Props) {
    const { useToken } = theme;
    const { token } = useToken();

    const secondaryColor = token.colorPrimary;

    return (
        <Space size="small">
            <UserAvatarWithEmail user={user} color={secondaryColor} />
        </Space>
    );
}
