import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { Button, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import type { PendingAction } from '@/types/pending-actions/pending-request-types';

type Props = {
    action: PendingAction;
    onAccept: (action: PendingAction) => void;
    onReject: (action: PendingAction) => void;
};

export function RequestActions({ action, onAccept, onReject }: Props) {
    const { t } = useTranslation();

    return (
        <Space size="small" onClick={(e) => e.stopPropagation()}>
            <Button type="primary" size="small" icon={<CheckOutlined />} onClick={() => onAccept(action)}>
                {t('Accept')}
            </Button>
            <Button danger size="small" icon={<CloseOutlined />} onClick={() => onReject(action)}>
                {t('Reject')}
            </Button>
        </Space>
    );
}
