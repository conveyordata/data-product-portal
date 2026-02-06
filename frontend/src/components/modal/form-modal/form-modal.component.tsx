import { Modal, type ModalProps, Typography } from 'antd';

type Props = ModalProps & {
    onClose?: () => void;
    isOpen?: boolean;
};

const titleComponent = ({ title }: Props) => {
    return <Typography.Title level={5}>{title}</Typography.Title>;
};

export function FormModal({ title, onClose, isOpen, ...modalProps }: Props) {
    function handleCloseModal() {
        onClose?.();
    }

    return (
        <Modal centered {...modalProps} title={titleComponent({ title })} open={isOpen} onCancel={handleCloseModal} />
    );
}
