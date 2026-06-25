import { Button, Tooltip } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { InputPortReasoningModal } from '@/components/input-port-reasoning-modal/input-port-reasoning-modal.tsx';

type Props = {
    reasoning?: string | null;
};

export function InputPortReasoningButton({ reasoning }: Props) {
    const { t } = useTranslation();

    const [showReasoning, setShowReasoning] = useState(false);
    return (
        <>
            <Tooltip
                title={reasoning === undefined || reasoning === null ? t('No reasoning provided') : t('Show reasoning')}
            >
                <Button
                    // type={'text'}
                    // icon={<CommentOutlined />}
                    disabled={!reasoning}
                    onClick={() => setShowReasoning(true)}
                >
                    {t('Show reasoning')}
                </Button>
            </Tooltip>

            {showReasoning && reasoning && (
                <InputPortReasoningModal reasoning={reasoning} onclose={() => setShowReasoning(false)} />
            )}
        </>
    );
}
