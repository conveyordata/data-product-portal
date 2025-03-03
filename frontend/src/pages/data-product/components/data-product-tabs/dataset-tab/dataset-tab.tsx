import { Button, Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { Searchbar } from '@/components/form';
import { useModal } from '@/hooks/use-modal.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { DatasetLink } from '@/types/data-product';
import { SearchForm } from '@/types/shared';
import { getIsDataProductOwner } from '@/utils/data-product-user-role.helper.ts';

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
    const { isVisible, handleOpen, handleClose } = useModal();
    const user = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDatasets = useMemo(() => {
        return filterDatasets(dataProduct?.dataset_links ?? [], searchTerm);
    }, [dataProduct?.dataset_links, searchTerm]);

    const isDataProductOwner = useMemo(() => {
        if (!dataProduct || !user) return false;

        return getIsDataProductOwner(dataProduct, user.id) || user.is_admin;
    }, [dataProduct, user]);

    return (
        <>
            <Flex vertical className={styles.container}>
                <Searchbar
                    placeholder={t('Search existing input datasets by name')}
                    formItemProps={{ initialValue: '' }}
                    form={searchForm}
                    actionButton={
                        <Button
                            disabled={!isDataProductOwner}
                            type={'primary'}
                            className={styles.formButton}
                            onClick={handleOpen}
                        >
                            {t('Add Dataset')}
                        </Button>
                    }
                />

                <DatasetTable
                    isCurrentDataProductOwner={isDataProductOwner}
                    dataProductId={dataProductId}
                    datasets={filteredDatasets}
                />
            </Flex>
            {isVisible && <AddDatasetPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />}
        </>
    );
}
