import { EyeOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import { useTranslation } from 'react-i18next';
import type { Request } from '@/types/request-types/request-types.tsx';

type Props = {
    action: Request;
    onReview: (action: Request) => void;
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
