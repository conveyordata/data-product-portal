import { Searchbar } from '@/components/form';
import { FormInstance } from 'antd';
import { FormModal } from '@/components/modal/form-modal/form-modal.component.tsx';
import { ReactNode } from 'react';
import styles from './data-product-dataset-link-popup.module.scss';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    searchForm: FormInstance;
    title: ReactNode;
    searchPlaceholder?: string;
    children: ReactNode;
};

export function DataProductDatasetLinkPopup({
    onClose,
    isOpen,
    searchForm,
    title,
    searchPlaceholder,
    children,
}: Props) {
    return (
        <FormModal title={title} onClose={onClose} isOpen={isOpen} footer={(_, { CancelBtn }) => <CancelBtn />}>
            <Searchbar form={searchForm} formItemProps={{ initialValue: '' }} placeholder={searchPlaceholder} />
            <div className={styles.list}>{children}</div>
        </FormModal>
    );
}
