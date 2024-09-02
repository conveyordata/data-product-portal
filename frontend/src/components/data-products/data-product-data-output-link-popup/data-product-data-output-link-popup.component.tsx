import { FormModal } from '@/components/modal/form-modal/form-modal.component.tsx';
import { ReactNode, RefObject } from 'react';
import styles from './data-product-data-output-link-popup.module.scss';
import { Button, FormInstance, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import { DataOutputCreateFormSchema } from '@/types/data-output';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    title: ReactNode;
    children: ReactNode;
    formRef: RefObject<FormInstance<DataOutputCreateFormSchema>>;
};

export function DataProductDataOutputLinkPopup({ onClose, isOpen, title, formRef, children }: Props) {
    const { t } = useTranslation();
    return (
        <FormModal
            title={title}
            onClose={onClose}
            onOk={() => {}}
            isOpen={isOpen}
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
        >
            <div className={styles.list}>{children}</div>
        </FormModal>
    );
}
