import { Button, Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { DatasetTable } from './components/dataset-table/dataset-table.component.tsx';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
// import { getIsDataOutputOwner } from '@/utils/data-output-user-role.helper.ts';
import { SearchForm } from '@/types/shared';
import styles from './dataset-tab.module.scss';
import { Searchbar } from '@/components/form';
import { useModal } from '@/hooks/use-modal.tsx';
import { AddDatasetPopup } from '../../../../data-product/components/data-product-tabs/data-output-tab/components/add-dataset-popup/add-dataset-popup.tsx'
import { DataOutputDatasetLink } from '@/types/data-output';
import { getIsDataOutputOwner } from '@/utils/data-output-user-role.helper.ts';

type Props = {
    dataOutputId: string;
};

function filterDatasets(datasetLinks: DataOutputDatasetLink[], searchTerm: string) {
    return (
        datasetLinks.filter(
            (datasetLink) =>
                datasetLink?.dataset?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                datasetLink?.dataset?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function DatasetTab({ dataOutputId }: Props) {
    const { isVisible, handleOpen, handleClose } = useModal();
    const user = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    const { data: dataOutput } = useGetDataOutputByIdQuery(dataOutputId);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDatasets = useMemo(() => {
        return filterDatasets(dataOutput?.dataset_links ?? [], searchTerm);
    }, [dataOutput?.dataset_links, searchTerm]);

    const isDataOutputOwner = useMemo(() => {
        if (!dataOutput || !user) return false;
        return getIsDataOutputOwner(dataOutput, user.id) || user.is_admin;
    }, [dataOutput?.id, user?.id]);

    return (
        <>
            <Flex vertical className={styles.container}>
                <Searchbar
                    placeholder={t('Search datasets by name')}
                    formItemProps={{ initialValue: '' }}
                    form={searchForm}
                    actionButton={
                        <Button
                            disabled={!isDataOutputOwner}
                            type={'primary'}
                            className={styles.formButton}
                            onClick={handleOpen}
                        >
                            {t('Add Dataset')}
                        </Button>
                    }
                />

                <DatasetTable
                    isCurrentDataOutputOwner={isDataOutputOwner}
                    dataOutputId={dataOutputId}
                    datasets={filteredDatasets}
                />
            </Flex>
            {isVisible && <AddDatasetPopup onClose={handleClose} isOpen={isVisible} dataOutputId={dataOutputId} />}
        </>
    );
}
