import { List, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

import type { DataProductRoleAssignmentContract } from '@/types/roles/role.contract';

const { Text } = Typography;

export function NodeContext({
    nodeId,
    getNodeDataForSideBar,
    className,
}: {
    nodeId: string | null;
    getNodeDataForSideBar: (nodeId: string) => {
        name: string;
        domain: string;
        assignments: DataProductRoleAssignmentContract[];
        description: string;
    } | null;
    className?: string;
}) {
    const { t } = useTranslation();
    if (!nodeId) return null;

    const nodeData = getNodeDataForSideBar(nodeId);
    if (!nodeData) return null;

    return (
        <div className={className}>
            <Text strong>{t('Name')}:</Text> {nodeData.name}
            <br />
            <Text strong>{t('Domain')}:</Text> {nodeData.domain}
            <br />
            <Text strong>{t('Description')}:</Text> {nodeData.description}
            <br />
            {nodeData.assignments?.length > 0 && (
                <>
                    <Text strong>{t('Members')}:</Text>
                    <List
                        dataSource={nodeData.assignments}
                        renderItem={(member: DataProductRoleAssignmentContract) => (
                            <List.Item key={member.id}>
                                {t('{{first_name}} {{last_name}} as {{role_name}}', {
                                    first_name: member.user.first_name,
                                    last_name: member.user.last_name,
                                    role_name: member.role.name,
                                })}
                            </List.Item>
                        )}
                    />
                </>
            )}
        </div>
    );
}
