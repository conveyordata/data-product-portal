import type { FormInstance } from 'antd';
import { useRef } from 'react';
import { useTranslation } from 'react-i18next';

import { DataOutputForm } from '@/components/data-products/data-output-form/data-output-form.component';
import { DataProductDataOutputLinkPopup } from '@/components/data-products/data-product-data-output-link-popup/data-product-data-output-link-popup.component';
import type { DataOutputConfiguration, DataOutputCreateFormSchema } from '@/types/data-output';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    dataProductId: string;
};

export function AddDataOutputPopup({ onClose, isOpen, dataProductId }: Props) {
    const { t } = useTranslation();
    const ref = useRef<FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>>(null);

    return (
        <DataProductDataOutputLinkPopup
            onClose={onClose}
            isOpen={isOpen}
            title={t('Add Technical Asset')}
            formRef={ref}
        >
            <DataOutputForm
                formRef={ref}
                modalCallbackOnSubmit={onClose}
                mode={'create'}
                dataProductId={dataProductId}
            />
        </DataProductDataOutputLinkPopup>
    );
}
