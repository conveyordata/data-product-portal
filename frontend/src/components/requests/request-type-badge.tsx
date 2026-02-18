import { TeamOutlined } from '@ant-design/icons';
import { Flex } from 'antd';
import { useTranslation } from 'react-i18next';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import type { PendingActionTypes } from '@/types/pending-actions/pending-actions';
import { isOutputPortRequest, isRoleRequest } from '../../utils/request-utils';

type Props = {
    type: PendingActionTypes;
};

export function RequestTypeBadge({ type }: Props) {
    const { t } = useTranslation();

    if (isOutputPortRequest(type)) {
        return (
            <Flex gap="small">
                <DatasetOutlined />
                {t('Output Port')}
            </Flex>
        );
    }

    if (isRoleRequest(type)) {
        return (
            <Flex gap="small">
                <TeamOutlined />
                {t('Team')}
            </Flex>
        );
    }

    return (
        <Flex gap="small">
            <DataProductOutlined />
            {t('Data Product')}
        </Flex>
    );
}
