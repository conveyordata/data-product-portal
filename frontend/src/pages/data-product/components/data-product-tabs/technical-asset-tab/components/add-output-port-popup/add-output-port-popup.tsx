import type { FormInstance } from 'antd';
import { useRef } from 'react';
import { useTranslation } from 'react-i18next';

import { DataProductLinkPopup } from '@/components/data-products/data-product-data-output-link-popup/data-product-data-output-link-popup.component';
import { OutputPortForm } from '@/components/output-ports/output-port-form/output-port-form.component';
import type { CreateOutputPortRequest } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    dataProductId: string;
};

export function AddOutputPortPopup({ onClose, isOpen, dataProductId }: Props) {
    const { t } = useTranslation();
    const ref = useRef<FormInstance<CreateOutputPortRequest>>(null);

    return (
        <DataProductLinkPopup onClose={onClose} isOpen={isOpen} title={t('Add Output Port')} formRef={ref}>
            <OutputPortForm formRef={ref} modalCallbackOnSubmit={onClose} mode="create" dataProductId={dataProductId} />
        </DataProductLinkPopup>
    );
}
