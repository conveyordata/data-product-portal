import { Badge, Flex } from 'antd';
import { useTranslation } from 'react-i18next';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import type { PendingActionTypes } from '@/types/pending-actions/pending-actions';
import { isOutputPortRequest } from '../../utils/request-utils';

type Props = {
    type: PendingActionTypes;
};

export function RequestTypeBadge({ type }: Props) {
    const { t } = useTranslation();

    if (isOutputPortRequest(type)) {
        return (
            <Badge
                count={
                    <Flex>
                        <DatasetOutlined style={{ fontSize: 12 }} />
                        {t('Output Port')}
                    </Flex>
                }
            />
        );
    }

    return (
        <Badge
            count={
                <Flex gap="small">
                    <DataProductOutlined style={{ fontSize: 12 }} />
                    {t('Data Product')}
                </Flex>
            }
        />
    );
}
