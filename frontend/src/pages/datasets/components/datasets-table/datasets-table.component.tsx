import { Button, Flex, Form, Input, Pagination, Space, Table, Typography } from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router';

import { RoleFilter } from '@/components/filters/role-filter.component';
import posthog from '@/config/posthog-config.ts';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { getDatasetTableColumns } from '@/pages/datasets/components/datasets-table/datasets-table-columns.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import type { DatasetsGetContract } from '@/types/dataset';
import { ApplicationPaths, createDatasetIdPath } from '@/types/navigation.ts';
import type { SearchForm } from '@/types/shared';
import styles from './datasets-table.module.scss';

function filterDatasets(datasets: DatasetsGetContract, searchTerm?: string) {
    if (!searchTerm) {
        return datasets;
    }
    return datasets.filter((dataset) => dataset.name.toLowerCase().includes(searchTerm.toLowerCase()));
}

function filterDatasetsByRoles(datasets: DatasetsGetContract, selectedDatasetIds: string[]) {
    if (!selectedDatasetIds.length) {
        return datasets;
    }

    return datasets.filter((dataset) => {
        return selectedDatasetIds.includes(dataset.id);
    });
}

export function DatasetsTable() {
    const currentUser = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [selectedDatasetIds, setSelectedDatasetIds] = useState<string[]>([]);
    const [selectedRole, setSelectedRole] = useState<string | undefined>(undefined);

    const { data: datasets = [], isFetching } = useGetAllDatasetsQuery();
    const { data: access } = useCheckAccessQuery(
        { action: AuthorizationAction.GLOBAL__CREATE_DATASET },
        { skip: !currentUser },
    );
    const canCreateDataset = access?.allowed || false;

    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDatasets = useMemo(() => {
        let filtered = filterDatasets(datasets, searchTerm);
        filtered = filterDatasetsByRoles(filtered, selectedDatasetIds);
        return filtered;
    }, [datasets, searchTerm, selectedDatasetIds]);

    const { pagination, handlePaginationChange } = useTablePagination(filteredDatasets);

    const columns = useMemo(() => getDatasetTableColumns({ t, datasets: filteredDatasets }), [t, filteredDatasets]);

    const CAPTURE_SEARCH_EVENT_DELAY = 750;

    useEffect(() => {
        if (searchTerm === undefined || searchTerm === '') return;

        const oldTerm = searchTerm;
        const timeoutId = setTimeout(() => {
            posthog.capture(PosthogEvents.MARKETPLACE_SEARCHED_DATASET, {
                search_term: oldTerm,
            });
        }, CAPTURE_SEARCH_EVENT_DELAY);

        return () => clearTimeout(timeoutId); // clear if searchTerm gets updated beforehand
    }, [searchTerm]);

    const handlePageChange = (page: number, pageSize: number) => {
        handlePaginationChange({
            ...pagination,
            current: page,
            pageSize,
        });
    };

    const handleRoleChange = (selected: { productIds: string[]; role: string }) => {
        setSelectedDatasetIds(selected.productIds);
        setSelectedRole(selected.role);
    };

    function navigateToDataset(datasetId: string) {
        navigate(createDatasetIdPath(datasetId));
    }

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
                    <RoleFilter mode={'datasets'} selectedRole={selectedRole} onRoleChange={handleRoleChange} />
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
