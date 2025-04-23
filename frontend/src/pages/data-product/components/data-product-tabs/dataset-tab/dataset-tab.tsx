import { Button, Col, Flex, Form, Pagination } from 'antd';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { Searchbar } from '@/components/form';
import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useModal } from '@/hooks/use-modal.tsx';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
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
    const { pagination, handlePaginationChange, resetPagination } = useTablePagination({
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

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

    const canCreateDatasetNew = access?.allowed || false;

    const isDataProductOwner = useMemo(() => {
        if (!dataProduct || !user) return false;

        return getIsDataProductOwner(dataProduct, user.id) || user.is_admin;
    }, [dataProduct, user]);

    const handlePageChange = (page: number, pageSize: number) => {
        handlePaginationChange({
            ...pagination,
            current: page,
            pageSize,
        });
    };

    useEffect(() => {
        resetPagination();
    }, [filteredDatasets, resetPagination]);

    return (
        <>
            <Flex vertical className={styles.container}>
                <Flex>
                    <Col span={20} className={styles.bar}>
                        <Searchbar
                            placeholder={t('Search existing input datasets by name')}
                            formItemProps={{ initialValue: '' }}
                            form={searchForm}
                            actionButton={
                                <Button
                                    disabled={!(canCreateDatasetNew || isDataProductOwner)}
                                    type={'primary'}
                                    className={styles.formButton}
                                    onClick={handleOpen}
                                >
                                    {t('Add Dataset')}
                                </Button>
                            }
                        />
                    </Col>
                    <Col span={4} className={styles.paginationBox}>
                        <Pagination
                            current={pagination.current}
                            pageSize={pagination.pageSize}
                            total={filteredDatasets.length}
                            onChange={handlePageChange}
                            size="small"
                        />
                    </Col>
                </Flex>

                <DatasetTable
                    isCurrentDataProductOwner={isDataProductOwner}
                    dataProductId={dataProductId}
                    datasets={filteredDatasets}
                    pagination={pagination}
                />
            </Flex>
            {isVisible && <AddDatasetPopup onClose={handleClose} isOpen={isVisible} dataProductId={dataProductId} />}
        </>
    );
}
