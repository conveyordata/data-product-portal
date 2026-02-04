import { Flex, Input, Radio, type RadioChangeEvent, Table } from 'antd';
import { parseAsBoolean, parseAsString, useQueryState } from 'nuqs';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router';

import { RoleFilter } from '@/components/filters/role-filter.component.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useGetAllDatasetsQuery, useGetUserDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import type { DatasetsGetContract } from '@/types/dataset/datasets-get.contract';
import { createDatasetIdPath } from '@/types/navigation.ts';
import styles from './output-ports-tab.module.scss';
import { getOutputPortTableColumns } from './output-ports-table-columns';

function filterOutputPorts(outputPorts: DatasetsGetContract, searchTerm?: string) {
    if (!searchTerm) {
        return outputPorts;
    }
    return outputPorts.filter(
        (outputPort) =>
            outputPort.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            outputPort.data_product_name.toLowerCase().includes(searchTerm.toLowerCase()),
    );
}

function filterOutputPortsByRoles(outputPorts: DatasetsGetContract, selectedPortIds: string[]) {
    if (!selectedPortIds.length) {
        return outputPorts;
    }

    return outputPorts.filter((outputPort) => {
        return selectedPortIds.includes(outputPort.id);
    });
}

export function OutputPortsTab() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);

    const [searchTerm, setSearchTerm] = useQueryState('search', parseAsString.withDefault(''));
    const [showAllPorts, setShowAllPorts] = useQueryState('showAll', parseAsBoolean.withDefault(false));
    const [selectedRole, setSelectedRole] = useQueryState('role', parseAsString);
    const [selectedPortIds, setSelectedPortIds] = useState<string[]>([]);

    const { data: userOutputPorts = [], isFetching: isFetchingUserPorts } = useGetUserDatasetsQuery(
        currentUser?.id || '',
        { skip: !currentUser || showAllPorts },
    );
    const { data: allOutputPorts = [], isFetching: isFetchingAllPorts } = useGetAllDatasetsQuery(undefined, {
        skip: !showAllPorts,
    });

    const outputPorts = showAllPorts ? allOutputPorts : userOutputPorts;
    const isFetching = showAllPorts ? isFetchingAllPorts : isFetchingUserPorts;

    const onSearch = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            setSearchTerm(e.target.value || null);
        },
        [setSearchTerm],
    );

    const filteredOutputPorts = useMemo(() => {
        let filtered = filterOutputPorts(outputPorts, searchTerm || undefined);
        filtered = filterOutputPortsByRoles(filtered, selectedPortIds);
        return filtered;
    }, [outputPorts, searchTerm, selectedPortIds]);

    const columns = useMemo(
        () => getOutputPortTableColumns({ t, outputPorts: filteredOutputPorts }),
        [t, filteredOutputPorts],
    );

    const navigateToOutputPort = (datasetId: string) => {
        navigate(createDatasetIdPath(datasetId));
    };

    const handleRoleChange = (selected: { productIds: string[]; role: string }) => {
        setSelectedPortIds(selected.productIds);
        setSelectedRole(selected.role || null);
    };

    const handleShowAllChange = (e: RadioChangeEvent) => {
        setShowAllPorts(e.target.value || null);
        // Reset role filter when switching between views
        setSelectedPortIds([]);
        setSelectedRole(null);
    };

    return (
        <Flex vertical gap="small">
            {/* Search and Filters */}
            <Flex justify="space-between" align="center">
                <Flex gap="middle" flex={1} align="center">
                    <Input.Search
                        placeholder={t('Search output ports by name or data product')}
                        value={searchTerm || ''}
                        onChange={onSearch}
                        allowClear
                        style={{ maxWidth: 400 }}
                    />
                    <RoleFilter
                        mode={'datasets'}
                        selectedRole={selectedRole || undefined}
                        onRoleChange={handleRoleChange}
                    />
                    <Radio.Group value={showAllPorts} onChange={handleShowAllChange} optionType="button">
                        <Radio.Button value={false}>{t('My Output Ports')}</Radio.Button>
                        <Radio.Button value={true}>{t('All Output Ports')}</Radio.Button>
                    </Radio.Group>
                </Flex>
            </Flex>

            {/* Pending Requests Section */}
            {/* TODO: Add pending requests specific to output ports */}

            {/* Table */}
            <Table
                onRow={(record) => ({
                    onClick: () => navigateToOutputPort(record.id),
                })}
                columns={columns}
                dataSource={filteredOutputPorts}
                pagination={{
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{total}} output ports', {
                            range0: range[0],
                            range1: range[1],
                            total: total,
                        }),
                }}
                rowKey={(record) => record.id}
                loading={isFetching}
                rowHoverable
                rowClassName={styles.row}
                size={'small'}
            />
        </Flex>
    );
}
