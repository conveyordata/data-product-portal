import { Button, type FormInstance, Space } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { Searchbar } from '@/components/form';
import { FormModal } from '@/components/modal/form-modal/form-modal.component.tsx';
import { ApplicationPaths } from '@/types/navigation';
import styles from './data-product-dataset-link-popup.module.scss';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    searchForm: FormInstance;
    title: ReactNode;
    searchPlaceholder?: string;
    children: ReactNode;
    canCreateDataset: boolean;
    dataProductId: string;
    dataOutputId: string;
};

export function DataProductDatasetLinkPopup({
    onClose,
    isOpen,
    searchForm,
    title,
    searchPlaceholder,
    children,
    canCreateDataset,
    dataProductId,
    dataOutputId,
}: Props) {
    const { t } = useTranslation();
    return (
        <FormModal title={title} onClose={onClose} isOpen={isOpen} footer={(_, { CancelBtn }) => <CancelBtn />}>
            <Space
                direction={'horizontal'}
                style={{ width: '100%', justifyContent: 'space-between', alignItems: 'center' }}
            >
                <Searchbar form={searchForm} formItemProps={{ initialValue: '' }} placeholder={searchPlaceholder} />
                <Link to={`${ApplicationPaths.DatasetNew}?dataProductId=${dataProductId}&dataOutputId=${dataOutputId}`}>
                    <Button className={styles.formButton} type={'primary'} disabled={!canCreateDataset}>
                        {t('Create Dataset')}
                    </Button>
                </Link>
            </Space>
            <div className={styles.list}>{children}</div>
        </FormModal>
    );
}
