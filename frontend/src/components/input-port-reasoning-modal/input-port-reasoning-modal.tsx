import { Modal } from 'antd';
import { useTranslation } from 'react-i18next';

type Props = {
    reasoning: string;
    onclose: () => void;
};

export function InputPortReasoningModal({ reasoning, onclose }: Props) {
    const { t } = useTranslation();
    return (
        <Modal
            open
            cancelButtonProps={{ style: { display: 'none' } }}
            onOk={() => onclose()}
            onCancel={() => onclose()}
            title={t('Reasoning')}
        >
            {reasoning}
        </Modal>
    );
}
