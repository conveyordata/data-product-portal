import { Button, Flex, Form, Input, Space, Table, type TableProps, Typography } from 'antd';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router';

import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { getPlatformConfigTableColumns } from '@/pages/platforms-configs/components/platforms-configs-table/platforms-configs-columns';
import { useGetAllPlatformsConfigsQuery } from '@/store/features/platform-service-configs/platform-service-configs-api-slice';
import { ApplicationPaths, createPlatformServiceConfigIdPath } from '@/types/navigation.ts';
import type { PlatformServiceConfigContract } from '@/types/platform-service-config';
import type { SearchForm } from '@/types/shared';

import styles from './platforms-configs-table.module.scss';

function filterPlatformConfigs(platformConfigs: PlatformServiceConfigContract[], searchTerm?: string) {
    if (!searchTerm) {
        return platformConfigs;
    }

    return platformConfigs.filter(
        (platformConfig) =>
            platformConfig.platformName.toLowerCase().includes(searchTerm.toLowerCase()) ||
            platformConfig.serviceName.toLowerCase().includes(searchTerm.toLowerCase()),
    );
}

export function PlatformsConfigsTable() {
    const { t } = useTranslation();
    const navigate = useNavigate();

    const columns = useMemo(() => getPlatformConfigTableColumns({ t }), [t]);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const { data = [], isFetching } = useGetAllPlatformsConfigsQuery();
    const platformsConfigs = data.map((item) => ({
        ...item,
        platformName: item.platform.name,
        serviceName: item.service.name,
    }));
    const filteredPlatformConfigs = useMemo(() => {
        return filterPlatformConfigs(platformsConfigs, searchTerm);
    }, [platformsConfigs, searchTerm]);
    const { pagination, handlePaginationChange, handleTotalChange } = useTablePagination(filteredPlatformConfigs);

    const onChange: TableProps<PlatformServiceConfigContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    function navigateToPlatformServiceConfig(configId: string) {
        navigate(createPlatformServiceConfigIdPath(configId));
    }

    useEffect(() => {
        if (!isFetching) {
            handleTotalChange(platformsConfigs.length);
        }
    }, [handleTotalChange, isFetching, platformsConfigs.length]);

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Platforms Configurations')}</Typography.Title>
                <Form<SearchForm> form={searchForm} className={styles.searchForm}>
                    <Form.Item<SearchForm> name={'search'} initialValue={''} className={styles.formItem}>
                        <Input.Search placeholder={t('Search configurations by platform or service name')} allowClear />
                    </Form.Item>
                </Form>
                <Space>
                    <Link to={ApplicationPaths.PlatformServiceConfigNew}>
                        <Button className={styles.formButton} type={'primary'}>
                            {t('Create configuration')}
                        </Button>
                    </Link>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Table<PlatformServiceConfigContract>
                    onRow={(record) => {
                        return {
                            onClick: () => navigateToPlatformServiceConfig(record.id),
                        };
                    }}
                    className={styles.table}
                    columns={columns}
                    dataSource={filteredPlatformConfigs}
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
