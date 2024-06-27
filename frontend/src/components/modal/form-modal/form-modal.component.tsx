import { Modal, ModalProps, Typography } from 'antd';
import styles from './form-modal.module.scss';

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
        <Modal
            className={styles.container}
            centered
            {...modalProps}
            title={titleComponent({ title })}
            open={isOpen}
            onCancel={handleCloseModal}
            classNames={{
                content: styles.formModalContent,
                header: styles.formModalHeader,
                body: styles.formModalBody,
            }}
        />
    );
}
