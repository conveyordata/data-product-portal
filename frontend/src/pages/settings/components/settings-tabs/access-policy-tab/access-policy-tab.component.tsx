import { Flex, theme } from 'antd';

import AccessDurations from '@/pages/settings/components/settings-tabs/access-policy-tab/access-durations.tsx';
import AccessModes from '@/pages/settings/components/settings-tabs/access-policy-tab/access-modes.tsx';
import { OutputPortAccessTypesTable } from '../components/output-port-access-types-table/output-port-access-types-table.component';

export function AccessPolicyTab() {
    const { token } = theme.useToken();

    return (
        <Flex vertical gap={token.sizeXL}>
            <AccessDurations />
            <OutputPortAccessTypesTable />
            <AccessModes />
        </Flex>
    );
}
