import { Button, Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Searchbar } from '@/components/form';
import { useModal } from '@/hooks/use-modal';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import type { DataOutputsGetContract } from '@/types/data-output/data-output-get.contract';
import type { SearchForm } from '@/types/shared';

import { AddDataOutputPopup } from './components/add-data-output-popup/add-data-output-popup';
import { DataOutputTable } from './components/data-output-table/data-output-table.component';
import { DatasetTable } from './components/dataset-table/dataset-table.component';
import styles from './data-output-tab.module.scss';

function filterDataOutputs(data_outputs: DataOutputsGetContract, searchTerm: string) {
    return (
        data_outputs.filter(
            (data_output) =>
                data_output?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                data_output?.namespace?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

type Props = {
    dataProductId: string;
};
export function DataOutputTab({ dataProductId }: Props) {
    const { t } = useTranslation();

    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDataOutputs = useMemo(() => {
        return filterDataOutputs(dataProduct?.data_outputs ?? [], searchTerm);
    }, [dataProduct?.data_outputs, searchTerm]);

    return (
        <>
            <Flex
                vertical
                className={`${styles.container} ${filteredDataOutputs.length === 0 && styles.paginationGap}`}
            >
                <Searchbar
                    placeholder={t('Search data outputs by name')}
                    formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                    form={searchForm}
                    // actionButton={
                    //     <Button
                    //         disabled={!canCreateDataOutput}
                    //         type={'primary'}
                    //         className={styles.formButton}
                    //         onClick={handleOpen}
                    //     >
                    //         {t('Add Data Output')}
                    //     </Button>
                    // }
                />
                <Flex>
                    <DatasetTable datasets={dataProduct?.datasets ?? []} dataProductId={dataProductId} />
                    <DataOutputTable dataProductId={dataProductId} dataOutputs={filteredDataOutputs} />
                </Flex>
            </Flex>
        </>
    );
}
