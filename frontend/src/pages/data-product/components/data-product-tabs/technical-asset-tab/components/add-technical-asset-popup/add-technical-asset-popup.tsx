import type { FormInstance } from 'antd';
import { useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { DataProductLinkPopup } from '@/components/data-products/data-product-data-output-link-popup/data-product-data-output-link-popup.component';
import { TechnicalAssetForm } from '@/components/data-products/technical-asset-form/technical-asset-form.component';
import type { CreateTechnicalAssetRequest } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    dataProductId: string;
    debounce?: number;
};

export function AddTechnicalAssetPopup({ onClose, isOpen, dataProductId, debounce }: Props) {
    const { t } = useTranslation();
    const ref = useRef<FormInstance<CreateTechnicalAssetRequest> | null>(null);

    return (
        <DataProductLinkPopup onClose={onClose} isOpen={isOpen} title={t('Add Technical Asset')} formRef={ref}>
            <TechnicalAssetForm
                formRef={ref}
                modalCallbackOnSubmit={onClose}
                mode="create"
                dataProductId={dataProductId}
                debounce={debounce}
            />
        </DataProductLinkPopup>
    );
}
