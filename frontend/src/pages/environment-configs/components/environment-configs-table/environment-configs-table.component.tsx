import { Button, Flex, Form, Input, Space, Table, TableProps, Typography } from 'antd';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router';

import { buildUrl } from '@/api/api-urls';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useGetAllEnvironmentConfigsQuery } from '@/store/features/environments/environments-api-slice';
import { EnvironmentConfigContract } from '@/types/environment';
import { ApplicationPaths, createEnvironmentConfigPath, DynamicPathParams } from '@/types/navigation';
import { SearchForm } from '@/types/shared';

import { getEnvironmentConfigTableColumns } from './environment-configs-columns';
import styles from './environment-configs-table.module.scss';

function filterEnvConfigs(envConfigs: EnvironmentConfigContract[], searchTerm?: string) {
    if (!searchTerm) {
        return envConfigs;
    }

    return envConfigs.filter(
        (envConfig) =>
            envConfig.platformName.toLowerCase().includes(searchTerm.toLowerCase()) ||
            envConfig.serviceName.toLowerCase().includes(searchTerm.toLowerCase()),
    );
}

export const EnvironmentConfigsTable = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { environmentId = '' } = useParams<DynamicPathParams>();

    const { pagination, handlePaginationChange, handleTotalChange } = useTablePagination({});

    const { data = [], isFetching } = useGetAllEnvironmentConfigsQuery(environmentId, {
        skip: !environmentId,
    });

    const envConfigs = data.map((item) => ({
        ...item,
        platformName: item.platform.name,
        serviceName: item.service.name,
    }));

    const columns = useMemo(() => getEnvironmentConfigTableColumns({ t }), [t]);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredEnvConfigs = useMemo(() => {
        return filterEnvConfigs(envConfigs, searchTerm);
    }, [envConfigs, searchTerm]);

    const onChange: TableProps<EnvironmentConfigContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    function navigateToEnvironmentConfig(envConfigId: string) {
        navigate(createEnvironmentConfigPath(envConfigId));
    }

    useEffect(() => {
        if (!isFetching) {
            handleTotalChange(envConfigs.length);
        }
    }, [envConfigs.length, handleTotalChange, isFetching]);

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Environment Configurations')}</Typography.Title>
                <Form<SearchForm> form={searchForm} className={styles.searchForm}>
                    <Form.Item<SearchForm> name={'search'} initialValue={''} className={styles.formItem}>
                        <Input.Search placeholder={t('Search configuration by platform or service name')} allowClear />
                    </Form.Item>
                </Form>
                <Space>
                    <Link to={buildUrl(ApplicationPaths.EnvironmentConfigNew, { environmentId })}>
                        <Button className={styles.formButton} type={'primary'}>
                            {t('Create configuration')}
                        </Button>
                    </Link>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Table<EnvironmentConfigContract>
                    onRow={(record) => {
                        return {
                            onClick: () => navigateToEnvironmentConfig(record.id),
                        };
                    }}
                    className={styles.table}
                    columns={columns}
                    dataSource={filteredEnvConfigs}
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
