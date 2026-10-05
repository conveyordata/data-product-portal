import { Flex, theme } from 'antd';

import AccessDurations from '@/pages/settings/components/settings-tabs/access-policy-tab/access-durations.tsx';
import AccessModes from '@/pages/settings/components/settings-tabs/access-policy-tab/access-modes.tsx';
import { useIsTimeBoundAccessEnabledQuery } from '@/store/api/services/generated/configurationAccessDurationsApi';
import { OutputPortAccessTypesTable } from '../components/output-port-access-types-table/output-port-access-types-table.component';

export function AccessPolicyTab() {
    const { token } = theme.useToken();
    const { data: isTimeBoundAccessEnabled } = useIsTimeBoundAccessEnabledQuery();

    return (
        <Flex vertical gap={token.sizeXL}>
            {isTimeBoundAccessEnabled?.enabled && <AccessDurations />}
            <OutputPortAccessTypesTable />
            <AccessModes />
        </Flex>
    );
}
