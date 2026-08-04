import { Button, type FormInstance, Modal, Space } from 'antd';
import type { ReactNode, RefObject } from 'react';
import { useTranslation } from 'react-i18next';

import styles from './data-product-data-output-link-popup.module.scss';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    title: ReactNode;
    children: ReactNode;
    formRef: RefObject<FormInstance | null>;
};

export function DataProductDataOutputLinkPopup({ onClose, isOpen, title, formRef, children }: Props) {
    const { t } = useTranslation();

    return (
        <Modal
            title={title}
            onCancel={onClose}
            open={isOpen}
            footer={() => (
                <Space>
                    <Button
                        className={styles.formButton}
                        type="primary"
                        htmlType={'submit'}
                        onClick={() => formRef.current?.submit()}
                    >
                        {t('Create')}
                    </Button>
                    <Button className={styles.formButton} type="default" onClick={onClose}>
                        {t('Cancel')}
                    </Button>
                </Space>
            )}
            centered
        >
            {children}
        </Modal>
    );
}
