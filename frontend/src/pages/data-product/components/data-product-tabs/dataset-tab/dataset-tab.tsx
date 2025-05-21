import { Button, Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Searchbar } from '@/components/form';
import { useModal } from '@/hooks/use-modal.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DatasetLink } from '@/types/data-product';
import type { SearchForm } from '@/types/shared';

import { AddDatasetPopup } from './components/add-dataset-popup/add-dataset-popup.tsx';
import { DatasetTable } from './components/dataset-table/dataset-table.component.tsx';
import styles from './dataset-tab.module.scss';

type Props = {
    dataProductId: string;
};

function filterDatasets(datasetLinks: DatasetLink[], searchTerm: string) {
    return (
        datasetLinks.filter(
            (datasetLink) =>
                datasetLink?.dataset?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                datasetLink?.dataset?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function DatasetTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { isVisible, handleOpen, handleClose } = useModal();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDatasets = useMemo(() => {
        return filterDatasets(dataProduct?.dataset_links ?? [], searchTerm);
    }, [dataProduct?.dataset_links, searchTerm]);

    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__REQUEST_DATASET_ACCESS,
        },
        { skip: !dataProductId },
    );

    const canCreateDataset = access?.allowed || false;

    return (
        <>
            <Flex vertical className={`${styles.container} ${filteredDatasets.length === 0 && styles.paginationGap}`}>
                <Searchbar
                    placeholder={t('Search existing input datasets by name')}
                    formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                    form={searchForm}
                    actionButton={
                        <Button
                            disabled={!canCreateDataset}
                            type={'primary'}
                            className={styles.formButton}
                            onClick={handleOpen}
                        >
                            {t('Add Dataset')}
                        </Button>
                    }
                />
                <DatasetTable dataProductId={dataProductId} datasets={filteredDatasets} />
            </Flex>
            {isVisible && <AddDatasetPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />}
        </>
    );
}
