import type { RadioChangeEvent, TableProps } from 'antd';
import { Button, Flex, Form, Input, Space, Table, Typography } from 'antd';
import styles from './data-outputs-table.module.scss';
import { Link, useNavigate } from 'react-router-dom';
import { ApplicationPaths, createDataOutputIdPath } from '@/types/navigation.ts';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { getDataOutputTableColumns } from '@/pages/data-outputs/components/data-outputs-table/data-outputs-table-columns.tsx';
import { DataOutputsGetContract } from '@/types/data-output';
import { SearchForm } from '@/types/shared';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { TableQuickFilter } from '@/components/list/table-quick-filter/table-quick-filter.tsx';
import { useQuickFilter } from '@/hooks/use-quick-filter.tsx';
import { QuickFilterParticipation } from '@/types/shared/table-filters.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useGetAllDataOutputsQuery } from '@/store/features/data-outputs/data-outputs-api-slice';

function filterDataOutputs(dataOutputs: DataOutputsGetContract, searchTerm?: string) {
    if (!searchTerm) {
        return dataOutputs;
    }
    return dataOutputs.filter((dataOutput) => dataOutput.name.toLowerCase().includes(searchTerm.toLowerCase()));
}

export function DataOutputsTable() {
    const currentUser = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    const { quickFilter, onQuickFilterChange, quickFilterOptions } = useQuickFilter({});
    const navigate = useNavigate();
    const { data: dataOutputs = [], isFetching } = useGetAllDataOutputsQuery();
    // const { data: userDataOutputs = [], isFetching: isFetchingUserDataOutputs } = useGetUserDataOutputsQuery(
    //     currentUser?.id || '',
    //     { skip: !currentUser },
    // );
    // TODO
    const isFetchingUserDataOutputs = false
    const userDataOutputs: DataOutputsGetContract = []
    const { pagination, handlePaginationChange, handleTotalChange, resetPagination } = useTablePagination({});
    const columns = useMemo(() => getDataOutputTableColumns({ t }), [t]);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDataOutputs = useMemo(() => {
        const data = quickFilter === QuickFilterParticipation.Me ? userDataOutputs : dataOutputs;
        return filterDataOutputs(data, searchTerm);
    }, [quickFilter, userDataOutputs, dataOutputs, searchTerm]);

    const onChange: TableProps<DataOutputsGetContract[0]>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    function navigateToDataOutput(dataOutputId: string) {
        navigate(createDataOutputIdPath(dataOutputId));
    }

    const handleQuickFilterChange = ({ target: { value } }: RadioChangeEvent) => {
        onQuickFilterChange(value);
        resetPagination();
    };

    useEffect(() => {
        if (!isFetching && !isFetchingUserDataOutputs) {
            if (quickFilter === QuickFilterParticipation.All) {
                handleTotalChange(dataOutputs.length);
            } else {
                handleTotalChange(userDataOutputs.length);
            }
        }
    }, [quickFilter, isFetching, isFetchingUserDataOutputs]);

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Data Outputs')}</Typography.Title>
                <Form<SearchForm> form={searchForm} className={styles.searchForm}>
                    <Form.Item<SearchForm> name={'search'} initialValue={''} className={styles.formItem}>
                        <Input.Search placeholder={t('Search data outputs by name')} allowClear />
                    </Form.Item>
                </Form>
                <Space>
                    <Link to={ApplicationPaths.DataOutputNew}>
                        <Button className={styles.formButton} type={'primary'}>
                            {t('Create Data Output')}
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
                <Table<DataOutputsGetContract[0]>
                    onRow={(record) => {
                        return {
                            onClick: () => navigateToDataOutput(record.id),
                        };
                    }}
                    className={styles.table}
                    columns={columns}
                    dataSource={filteredDataOutputs}
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
