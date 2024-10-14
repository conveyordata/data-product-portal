import { useGetAllDatasetsQuery, useGetUserDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import styles from './datasets-table.module.scss';
import { Button, Flex, Form, Input, RadioChangeEvent, Space, Table, TableProps, Typography } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import { ApplicationPaths, createDatasetIdPath } from '@/types/navigation.ts';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { getDatasetTableColumns } from '@/pages/datasets/components/datasets-table/datasets-table-columns.tsx';
import { DatasetsGetContract } from '@/types/dataset';
import { SearchForm } from '@/types/shared';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useSelector } from 'react-redux';
import { useQuickFilter } from '@/hooks/use-quick-filter.tsx';
import { QuickFilterParticipation } from '@/types/shared/table-filters.ts';
import { TableQuickFilter } from '@/components/list/table-quick-filter/table-quick-filter.tsx';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';

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
    const { pagination, handlePaginationChange, handleTotalChange, resetPagination } = useTablePagination({});
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDatasets = useMemo(() => {
        const data = quickFilter === QuickFilterParticipation.All ? datasets : userDatasets;
        return filterDatasets(data, searchTerm);
    }, [quickFilter, datasets, userDatasets, searchTerm]);

    const columns = useMemo(() => getDatasetTableColumns({ t, datasets: filteredDatasets }), [t, filteredDatasets]);

    const onChange: TableProps<DatasetsGetContract[0]>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
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
            if (quickFilter === QuickFilterParticipation.All) {
                handleTotalChange(datasets.length);
            } else {
                handleTotalChange(userDatasets.length);
            }
        }
    }, [quickFilter, isFetching, isFetchingUserDatasets]);

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
                        <Button className={styles.formButton} type={'primary'}>
                            {t('Create Dataset')}
                        </Button>
                    </Link>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <TableQuickFilter
                    value={quickFilter}
                    onFilterChange={handleQuickFilterChange}
                    quickFilterOptions={quickFilterOptions}
                />
                <Table<DatasetsGetContract[0]>
                    onRow={(record) => {
                        return {
                            onClick: () => navigateToDataset(record.id),
                        };
                    }}
                    className={styles.table}
                    columns={columns}
                    dataSource={filteredDatasets}
                    onChange={onChange}
                    pagination={pagination}
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
