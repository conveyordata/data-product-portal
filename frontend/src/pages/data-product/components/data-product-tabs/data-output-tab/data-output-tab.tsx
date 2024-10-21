import { Button, Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { getIsDataProductOwner } from '@/utils/data-product-user-role.helper.ts';
import { SearchForm } from '@/types/shared';
import styles from './data-output-tab.module.scss';
import { Searchbar } from '@/components/form';
import { useModal } from '@/hooks/use-modal.tsx';
import { DataOutputTable } from './components/data-output-table/data-output-table.component';
import { AddDataOutputPopup } from './components/add-data-output-popup/add-data-output-popup';
import { DataOutputsGetContract } from '@/types/data-output/data-output-get.contract';

type Props = {
    dataProductId: string;
};

function filterDataOutputs(data_outputs: DataOutputsGetContract, searchTerm: string) {
    return (
        data_outputs.filter(
            (data_output) =>
                data_output?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                data_output?.external_id?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function DataOutputTab({ dataProductId }: Props) {
    const { isVisible, handleOpen, handleClose } = useModal();
    const user = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDataOutputs = useMemo(() => {
        return filterDataOutputs(dataProduct?.data_outputs ?? [], searchTerm);
    }, [dataProduct?.data_outputs, searchTerm]);

    const isDataProductOwner = useMemo(() => {
        if (!dataProduct || !user) return false;

        return getIsDataProductOwner(dataProduct, user.id) || user.is_admin;
    }, [dataProduct?.id, user?.id]);

    return (
        <>
            <Flex vertical className={styles.container}>
                <Searchbar
                    placeholder={t('Search data outputs by name')}
                    formItemProps={{ initialValue: '' }}
                    form={searchForm}
                    actionButton={
                        <Button
                            disabled={!isDataProductOwner}
                            type={'primary'}
                            className={styles.formButton}
                            onClick={handleOpen}
                        >
                            {t('Add Data Output')}
                        </Button>
                    }
                />

                <DataOutputTable
                    isCurrentDataProductOwner={isDataProductOwner}
                    dataProductId={dataProductId}
                    dataOutputs={filteredDataOutputs}
                />
            </Flex>
            {isVisible && <AddDataOutputPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />}
        </>
    );
}
