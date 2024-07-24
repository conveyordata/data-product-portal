
import { FormModal } from '@/components/modal/form-modal/form-modal.component.tsx';
import { ReactNode } from 'react';
import styles from './data-product-data-output-link-popup.module.scss';

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
    return (
        <FormModal title={title} onClose={onClose} isOpen={isOpen} footer={(_, { CancelBtn }) => <CancelBtn />}>
            <div className={styles.list}>{children}</div>
        </FormModal>
    );
}
