import { useTranslation } from 'react-i18next';
import { DataProductDataOutputLinkPopup } from '@/components/data-products/data-product-data-output-link-popup/data-product-data-output-link-popup.component.tsx';
import { DataOutputForm } from '@/components/data-products/data-output-form/data-output-form.component';
import { useRef } from 'react';
import { FormInstance } from 'antd';
import { DataOutputConfiguration, DataOutputCreateFormSchema } from '@/types/data-output';
import styles from './add-data-output-popup.module.scss';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    dataProductId: string;
};

export function AddDataOutputPopup({ onClose, isOpen, dataProductId }: Props) {
    const { t } = useTranslation();
    const ref = useRef<FormInstance<DataOutputCreateFormSchema&DataOutputConfiguration>>(null);

    return (
        <DataProductDataOutputLinkPopup
            onClose={onClose}
            isOpen={isOpen}
            title={t('Add Data Output')}
            formRef={ref}
        >
            <DataOutputForm formRef={ref} modalCallbackOnSubmit={onClose} mode={'create'} dataProductId={dataProductId} />
        </DataProductDataOutputLinkPopup>
    );
}
