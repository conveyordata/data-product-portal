import { Button, Flex, Input, Radio, Table } from 'antd';
import { parseAsBoolean, parseAsString, useQueryState } from 'nuqs';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router';
import { EmptyState } from '@/components/empty-state/empty-state.component.tsx';
import { ExplorationOutlined } from '@/components/icons';
import { getExplorationTableColumns } from '@/pages/product-studio/components/explorations-tab/explorations-table-columns.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { type Exploration, useGetExplorationsQuery } from '@/store/api/services/generated/explorationsApi.ts';
import { ApplicationPaths, createExplorationIdPath } from '@/types/navigation.ts';
import styles from './explorations-tab.module.scss';

function filterExplorations(explorations: Exploration[], searchTerm?: string) {
    if (!searchTerm) {
        return explorations;
    }
    return explorations.filter((exploration) => exploration.name.toLowerCase().includes(searchTerm.toLowerCase()));
}

export function ExplorationsTab() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);

    const [searchTerm, setSearchTerm] = useQueryState('search', parseAsString.withDefault(''));
    const [showAll, setShowAll] = useQueryState('showAll', parseAsBoolean.withDefault(false));

    const { data: { explorations = [] } = {}, isFetching } = useGetExplorationsQuery(
        showAll ? undefined : currentUser?.id,
    );

    const onSearch = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            setSearchTerm(e.target.value || null);
        },
        [setSearchTerm],
    );

    const columns = useMemo(() => getExplorationTableColumns({ t, explorations }), [t, explorations]);

    const filteredExplorations = useMemo(() => {
        return filterExplorations(explorations, searchTerm || undefined);
    }, [explorations, searchTerm]);

    const navigateToExploration = (explorationId: string) => {
        navigate(createExplorationIdPath(explorationId));
    };

    return (
        <Flex vertical gap="small">
            <Flex gap="middle" align="center">
                <Input.Search
                    placeholder={t('Search Explorations by name')}
                    value={searchTerm ?? ''}
                    onChange={onSearch}
                    allowClear
                    style={{ maxWidth: 400 }}
                />
                <Radio.Group
                    value={showAll}
                    onChange={(e) => {
                        setShowAll(e.target.value);
                    }}
                    optionType="button"
                >
                    <Radio.Button value={false}>{t('My Explorations')}</Radio.Button>
                    <Radio.Button value={true}>{t('All Explorations')}</Radio.Button>
                </Radio.Group>
            </Flex>
            <Table<Exploration>
                onRow={(record) => ({
                    onClick: () => navigateToExploration(record.id),
                })}
                rowClassName={styles.row}
                columns={columns}
                dataSource={filteredExplorations}
                pagination={{
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{count}} Explorations', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                }}
                rowKey={(record) => record.id}
                loading={isFetching}
                rowHoverable
                size="small"
                locale={{
                    emptyText: (
                        <EmptyState
                            icon={<ExplorationOutlined />}
                            title={t('No Explorations yet')}
                            description={t(
                                'An Exploration is your own workspace on data you have access to. Find an Output Port in the Marketplace to start one.',
                            )}
                            action={
                                <Link to={ApplicationPaths.Marketplace}>
                                    <Button type="primary">{t('Browse Marketplace')}</Button>
                                </Link>
                            }
                            searchTerm={searchTerm ?? undefined}
                            subject={t('Explorations')}
                        />
                    ),
                }}
            />
        </Flex>
    );
}
