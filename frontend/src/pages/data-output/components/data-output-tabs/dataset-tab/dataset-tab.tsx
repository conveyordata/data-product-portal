import { Button, Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Searchbar } from '@/components/form';
import { useModal } from '@/hooks/use-modal.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DataOutputDatasetLink } from '@/types/data-output';
import type { SearchForm } from '@/types/shared';

import { AddDatasetPopup } from '../../../../data-product/components/data-product-tabs/data-output-tab/components/add-dataset-popup/add-dataset-popup.tsx';
import { DatasetTable } from './components/dataset-table/dataset-table.component.tsx';
import styles from './dataset-tab.module.scss';

function filterDatasets(datasetLinks: DataOutputDatasetLink[], searchTerm: string) {
    return (
        datasetLinks.filter(
            (datasetLink) =>
                datasetLink?.dataset?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                datasetLink?.dataset?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

type Props = {
    dataOutputId: string;
};
export function DatasetTab({ dataOutputId }: Props) {
    const { t } = useTranslation();
    const { isVisible, handleOpen, handleClose } = useModal();

    const { data: dataOutput, isFetching: isFetchingInitialValues } = useGetDataOutputByIdQuery(dataOutputId || '', {
        skip: !dataOutputId,
    });
    const { data: dataProduct } = useGetDataProductByIdQuery(dataOutput?.owner.id ?? '', {
        skip: !dataOutput?.owner.id || isFetchingInitialValues || !dataOutputId,
    });

    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);
    const filteredDatasets = useMemo(() => {
        return filterDatasets(dataOutput?.dataset_links ?? [], searchTerm);
    }, [dataOutput?.dataset_links, searchTerm]);

    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProduct?.id,
            action: AuthorizationAction.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
        },
        { skip: !dataProduct },
    );
    const canAddDataset = access?.allowed || false;

    return (
        <>
            <Flex vertical className={`${styles.container} ${filteredDatasets.length === 0 && styles.paginationGap}`}>
                <Searchbar
                    placeholder={t('Search datasets by name')}
                    formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                    form={searchForm}
                    actionButton={
                        <Button
                            disabled={!canAddDataset}
                            type={'primary'}
                            className={styles.formButton}
                            onClick={handleOpen}
                        >
                            {t('Add Dataset')}
                        </Button>
                    }
                />

                <DatasetTable dataProductId={dataProduct?.id} dataOutputId={dataOutputId} datasets={filteredDatasets} />
            </Flex>
            {isVisible && <AddDatasetPopup onClose={handleClose} isOpen={isVisible} dataOutputId={dataOutputId} />}
        </>
    );
}
