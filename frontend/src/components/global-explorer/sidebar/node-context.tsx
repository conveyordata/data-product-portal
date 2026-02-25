import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';

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
        </div>
    );
}
