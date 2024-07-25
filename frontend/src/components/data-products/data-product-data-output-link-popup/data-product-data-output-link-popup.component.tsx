
import { FormModal } from '@/components/modal/form-modal/form-modal.component.tsx';
import { ReactNode } from 'react';
import styles from './data-product-data-output-link-popup.module.scss';
import { Button, Space } from 'antd';
import { useTranslation } from 'react-i18next';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    title: ReactNode;
    children: ReactNode;
};

export function DataProductDataOutputLinkPopup({
    onClose,
    isOpen,
    title,
    children,
}: Props) {
    const { t } = useTranslation();
    return (
        <FormModal title={title} onClose={onClose} onOk={() => {}} isOpen={isOpen} footer={(_, { CancelBtn }) =>
            <Space>
                <Button
                    className={styles.formButton}
                    type="primary"
                    htmlType={'submit'}
                    // TODO Submit functionality
                    //loading={isCreating}
                    //disabled={isLoading || !canFillInForm}
                >
                    {t('Create')}
                </Button>
                <Button
                    className={styles.formButton}
                    type="default"
                    onClick={onClose}
                    //loading={isCreating}
                    //disabled={isLoading || !canFillInForm}
                >
                    {t('Cancel')}
                </Button>
            </Space>
        }>
            <div className={styles.list}>{children}</div>
        </FormModal>
    );
}
