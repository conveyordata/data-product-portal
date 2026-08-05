import { Flex } from 'antd';

import AccessDurations from '@/pages/settings/components/settings-tabs/access-policy-tab/access-durations.tsx';
import AccessModes from '@/pages/settings/components/settings-tabs/access-policy-tab/access-modes.tsx';

export function AccessPolicyTab() {
    return (
        <Flex vertical gap="large">
            <AccessDurations />
            <AccessModes />
        </Flex>
    );
}
