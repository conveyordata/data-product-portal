import { Button, Flex, Form, Input, Space, Table, type TableProps, Typography } from 'antd';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router';

import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useGetAllEnvironmentsQuery } from '@/store/features/environments/environments-api-slice.tsx';
import type { Environment } from '@/types/environment';
import { ApplicationPaths, createEnvironmentConfigsPath } from '@/types/navigation';
import type { SearchForm } from '@/types/shared';

import { getEnvironmentTableColumns } from './environments-columns';
import styles from './environments-table.module.scss';

function filterEnvironments(environments: Environment[], searchTerm?: string) {
    if (!searchTerm) {
        return environments;
    }

    return environments.filter((env) => env.name.toLowerCase().includes(searchTerm.toLowerCase()));
}

export const EnvironmentsTable = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { data: environments = [], isFetching } = useGetAllEnvironmentsQuery();

    const columns = useMemo(() => getEnvironmentTableColumns({ t }), [t]);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredEnvironments = useMemo(() => {
        return filterEnvironments(environments, searchTerm);
    }, [environments, searchTerm]);
    const { pagination, handlePaginationChange, handleTotalChange } = useTablePagination(filteredEnvironments);

    const onChange: TableProps<Environment>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    function navigateToEnvironmentConfigs(environmentId: string) {
        navigate(createEnvironmentConfigsPath(environmentId));
    }

    useEffect(() => {
        if (!isFetching) {
            handleTotalChange(environments.length);
        }
    }, [environments.length, handleTotalChange, isFetching]);

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Environments')}</Typography.Title>
                <Form<SearchForm> form={searchForm} className={styles.searchForm}>
                    <Form.Item<SearchForm> name={'search'} initialValue={''} className={styles.formItem}>
                        <Input.Search placeholder={t('Search environment by name')} allowClear />
                    </Form.Item>
                </Form>
                <Space>
                    <Link to={ApplicationPaths.EnvironmentNew}>
                        <Button className={styles.formButton} type={'primary'}>
                            {t('Create Environment')}
                        </Button>
                    </Link>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Table<Environment>
                    onRow={(record) => {
                        return {
                            onClick: () => navigateToEnvironmentConfigs(record.id),
                        };
                    }}
                    className={styles.table}
                    columns={columns}
                    dataSource={filteredEnvironments}
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
};
