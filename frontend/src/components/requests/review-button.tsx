import { EyeOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import { useTranslation } from 'react-i18next';
import type { PendingAction } from '@/types/pending-actions/pending-request-types';

type Props = {
    action: PendingAction;
    onReview: (action: PendingAction) => void;
};

export function ReviewButton({ action, onReview }: Props) {
    const { t } = useTranslation();

    return (
        <Button
            type="primary"
            size="small"
            icon={<EyeOutlined />}
            onClick={(e) => {
                e.stopPropagation();
                onReview(action);
            }}
        >
            {t('Review')}
        </Button>
    );
}
