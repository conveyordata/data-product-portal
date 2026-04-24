import { ToolOutlined } from '@ant-design/icons';
import { Button, Empty, Flex, Input, Table } from 'antd';
import Paragraph from 'antd/es/typography/Paragraph';
import { parseAsString, useQueryState } from 'nuqs';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router';
import { getExplorationTableColumns } from '@/pages/product-studio/components/explorations-tab/explorations-table-columns.tsx';
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

    const [searchTerm, setSearchTerm] = useQueryState('search', parseAsString.withDefault(''));

    const { data: { explorations = [] } = {}, isFetching } = useGetExplorationsQuery();

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
            <Flex justify="space-between" align="center">
                <Input.Search
                    placeholder={t('Search Explorations by name')}
                    value={searchTerm ?? ''}
                    onChange={onSearch}
                    allowClear
                    style={{ maxWidth: 400 }}
                />
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
                size={'small'}
                locale={{
                    emptyText: (
                        <Empty
                            styles={{ image: { height: 50 } }}
                            image={<ToolOutlined style={{ fontSize: 50 }} />}
                            description={
                                <>
                                    <Paragraph style={{ marginTop: 0, opacity: 0.45 }}>
                                        {t('Ready to Explore data?')}
                                    </Paragraph>
                                    <Paragraph style={{ opacity: 0.45 }}>
                                        {t(
                                            "It looks like you don't have any Explorations yet. Go to marketplace to shop and create one.",
                                        )}
                                    </Paragraph>
                                    <Link to={ApplicationPaths.Marketplace}>
                                        <Button type="primary">{t('Marketplace')}</Button>
                                    </Link>
                                </>
                            }
                        />
                    ),
                }}
            />
        </Flex>
    );
}
