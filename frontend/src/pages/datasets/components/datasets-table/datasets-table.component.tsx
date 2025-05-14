import { Button, Flex, Form, Input, Pagination, RadioChangeEvent, Space, Table, Typography } from 'antd';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router';

import { TableQuickFilter } from '@/components/list/table-quick-filter/table-quick-filter.tsx';
import { useQuickFilter } from '@/hooks/use-quick-filter.tsx';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { getDatasetTableColumns } from '@/pages/datasets/components/datasets-table/datasets-table-columns.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetAllDatasetsQuery, useGetUserDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { DatasetsGetContract } from '@/types/dataset';
import { ApplicationPaths, createDatasetIdPath } from '@/types/navigation.ts';
import { SearchForm } from '@/types/shared';
import { QuickFilterParticipation } from '@/types/shared/table-filters.ts';

import styles from './datasets-table.module.scss';

function filterDatasets(datasets: DatasetsGetContract, searchTerm?: string) {
    if (!searchTerm) {
        return datasets;
    }
    return datasets.filter((dataset) => dataset.name.toLowerCase().includes(searchTerm.toLowerCase()));
}

export function DatasetsTable() {
    const currentUser = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    const { quickFilter, onQuickFilterChange, quickFilterOptions } = useQuickFilter({});
    const navigate = useNavigate();
    const { data: datasets = [], isFetching } = useGetAllDatasetsQuery();
    const { data: userDatasets = [], isFetching: isFetchingUserDatasets } = useGetUserDatasetsQuery(
        currentUser?.id || '',
        { skip: !currentUser },
    );
    const { data: access } = useCheckAccessQuery(
        { action: AuthorizationAction.GLOBAL__CREATE_DATASET },
        { skip: !currentUser },
    );
    const canCreateDataset = access?.allowed || false;
    const { pagination, handlePaginationChange, resetPagination } = useTablePagination({});
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDatasets = useMemo(() => {
        const data = quickFilter === QuickFilterParticipation.All ? datasets : userDatasets;
        return filterDatasets(data, searchTerm);
    }, [quickFilter, datasets, userDatasets, searchTerm]);

    const columns = useMemo(() => getDatasetTableColumns({ t, datasets: filteredDatasets }), [t, filteredDatasets]);

    const handlePageChange = (page: number, pageSize: number) => {
        handlePaginationChange({
            ...pagination,
            current: page,
            pageSize,
        });
    };

    const handleQuickFilterChange = ({ target: { value } }: RadioChangeEvent) => {
        onQuickFilterChange(value);
        resetPagination();
    };

    function navigateToDataset(datasetId: string) {
        navigate(createDatasetIdPath(datasetId));
    }

    useEffect(() => {
        if (!isFetching && !isFetchingUserDatasets) {
            resetPagination();
        }
    }, [filteredDatasets, isFetching, isFetchingUserDatasets, resetPagination]);

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Datasets')}</Typography.Title>
                <Form<SearchForm> form={searchForm} className={styles.searchForm}>
                    <Form.Item<SearchForm> name={'search'} initialValue={''} className={styles.formItem}>
                        <Input.Search placeholder={t('Search datasets by name')} allowClear />
                    </Form.Item>
                </Form>
                <Space>
                    <Link to={ApplicationPaths.DatasetNew}>
                        <Button className={styles.formButton} type={'primary'} disabled={!canCreateDataset}>
                            {t('Create Dataset')}
                        </Button>
                    </Link>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Flex align="flex-end" justify="space-between" className={styles.tableBar}>
                    <TableQuickFilter
                        value={quickFilter}
                        onFilterChange={handleQuickFilterChange}
                        quickFilterOptions={quickFilterOptions}
                    />
                    <Pagination
                        current={pagination.current}
                        pageSize={pagination.pageSize}
                        total={filteredDatasets.length}
                        onChange={handlePageChange}
                        size="small"
                        showTotal={(total, range) =>
                            t('Showing {{range0}}-{{range1}} of {{total}} datasets', {
                                range0: range[0],
                                range1: range[1],
                                total: total,
                            })
                        }
                    />
                </Flex>
                <Table<DatasetsGetContract[0]>
                    onRow={(record) => {
                        return {
                            onClick: () => navigateToDataset(record.id),
                        };
                    }}
                    className={styles.table}
                    columns={columns}
                    dataSource={filteredDatasets}
                    pagination={{
                        ...pagination,
                        position: [],
                    }}
                    rowKey={(record) => record.id}
                    loading={isFetching}
                    rowHoverable
                    rowClassName={styles.row}
                    size={'small'}
                />
            </Flex>
        </Flex>
    );
}
