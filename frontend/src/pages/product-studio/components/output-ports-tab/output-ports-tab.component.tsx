import { DeploymentUnitOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Button, Empty, Flex, Input, Radio, type RadioChangeEvent, Table } from 'antd';
import Paragraph from 'antd/es/typography/Paragraph';
import { parseAsBoolean, parseAsString, useQueryState } from 'nuqs';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router';
import { RoleFilter } from '@/components/filters/role-filter.component.tsx';
import { PosthogEvents } from '@/constants/posthog.constants';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useListOutputPortRoleAssignmentsQuery } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetAllDatasetsQuery, useGetUserDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import type { DatasetsGetContract } from '@/types/dataset/datasets-get.contract';
import { ApplicationPaths, createDatasetIdPath } from '@/types/navigation.ts';
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
    const posthog = usePostHog();
    const { t } = useTranslation();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);

    const [searchTerm, setSearchTerm] = useQueryState('op-search', parseAsString.withDefault(''));
    const [showAllPorts, setShowAllPorts] = useQueryState('op-showAll', parseAsBoolean.withDefault(false));
    const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
    const [selectedPortIds, setSelectedPortIds] = useState<string[]>([]);
    const [isInitialized, setIsInitialized] = useState(false);

    // Fetch user's role assignments to find the Owner role
    const { data: userDatasetRoles } = useListOutputPortRoleAssignmentsQuery(
        { userId: currentUser?.id ?? '' },
        { skip: !currentUser },
    );

    // Set default to Owner role on initial load
    useEffect(() => {
        if (isInitialized || !userDatasetRoles?.role_assignments) {
            return;
        }

        // Find the Owner role
        const ownerAssignments = userDatasetRoles.role_assignments.filter(
            (assignment) => assignment.role?.name?.toLowerCase() === 'owner',
        );

        if (ownerAssignments.length > 0) {
            const ownerRoleId = ownerAssignments[0].role?.id ?? '';
            const ownerPortIds = ownerAssignments.map((assignment) => assignment.output_port.id);

            setSelectedRoles([ownerRoleId]);
            setSelectedPortIds(ownerPortIds);
        }

        setIsInitialized(true);
    }, [userDatasetRoles, isInitialized]);

    const { data: userOutputPorts = [], isFetching: isFetchingUserPorts } = useGetUserDatasetsQuery(
        currentUser?.id ?? '',
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
    const { data: access } = useCheckAccessQuery({ action: AuthorizationAction.GLOBAL__CREATE_DATAPRODUCT });
    const canCreateDataProduct = access?.allowed ?? false;
    const navigateToOutputPort = (datasetId: string) => {
        navigate(createDatasetIdPath(datasetId));
    };

    const handleRoleChange = (selected: { productIds: string[]; roles: string[] }) => {
        setSelectedPortIds(selected.productIds);
        setSelectedRoles(selected.roles);
        // Switch to "My Output Ports" when roles are selected
        if (selected.roles.length > 0) {
            setShowAllPorts(false);
        }
    };

    const handleShowAllChange = (e: RadioChangeEvent) => {
        setShowAllPorts(e.target.value || null);
        // Reset role filter when switching between views
        setSelectedPortIds([]);
        setSelectedRoles([]);
    };
    const createDataProductButton = (
        <Link
            to={ApplicationPaths.DataProductNew}
            onClick={() => posthog.capture(PosthogEvents.CREATE_DATA_PRODUCT_STARTED)}
        >
            <Button type={'primary'} disabled={!canCreateDataProduct}>
                {t('Create a Data Product first')}
            </Button>
        </Link>
    );

    return (
        <Flex vertical gap="small">
            {/* Search and Filters */}
            <Flex justify="space-between" align="center">
                <Flex gap="middle" flex={1} align="center">
                    <Input.Search
                        placeholder={t('Search Output Ports by name or Data Product')}
                        value={searchTerm ?? ''}
                        onChange={onSearch}
                        allowClear
                        style={{ maxWidth: 400 }}
                    />
                    <Radio.Group value={showAllPorts} onChange={handleShowAllChange} optionType="button">
                        <Radio.Button value={true}>{t('All Output Ports')}</Radio.Button>
                        <Radio.Button value={false}>{t('My Output Ports')}</Radio.Button>
                    </Radio.Group>
                    {!showAllPorts && (
                        <RoleFilter mode={'datasets'} selectedRoles={selectedRoles} onRoleChange={handleRoleChange} />
                    )}
                </Flex>
            </Flex>

            {/* Pending Requests Section */}
            {/* TODO: Add pending requests specific to Output Ports */}

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
                        t('Showing {{range0}}-{{range1}} of {{count}} Output Ports', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                }}
                rowKey={(record) => record.id}
                loading={isFetching}
                rowHoverable
                rowClassName={styles.row}
                size={'small'}
                locale={{
                    emptyText: (
                        <Empty
                            styles={{ image: { height: 50 } }}
                            image={<DeploymentUnitOutlined style={{ fontSize: 50 }} />}
                            description={
                                <>
                                    <Paragraph style={{ marginTop: 0, opacity: 0.45 }}>
                                        {t('Share your data with the organisation')}
                                    </Paragraph>
                                    <Paragraph style={{ opacity: 0.45 }}>
                                        {t(
                                            'Output Ports are a way for others to access a flavour of your Data Product. You can select an existing Data Product to add a new flavour to it or create a new Data Product to get started.',
                                        )}
                                    </Paragraph>
                                    {createDataProductButton}
                                </>
                            }
                        />
                    ),
                }}
            />
        </Flex>
    );
}
