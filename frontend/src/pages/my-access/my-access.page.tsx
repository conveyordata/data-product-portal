import { KeyOutlined, ShopOutlined } from '@ant-design/icons';
import { Button, Empty, Flex, Input, Table } from 'antd';
import Paragraph from 'antd/es/typography/Paragraph';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys.ts';
import {
    type EphemeralAccessResponse,
    useListEphemeralAccessQuery,
    usePromoteEphemeralAccessMutation,
    useRevokeEphemeralAccessMutation,
} from '@/store/api/services/generated/ephemeralAccessApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import { getMyAccessTableColumns } from './my-access-table-columns.tsx';

function filterItems(items: EphemeralAccessResponse[], searchTerm: string): EphemeralAccessResponse[] {
    if (!searchTerm) return items;
    const lower = searchTerm.toLowerCase();
    return items.filter(
        (item) =>
            item.name.toLowerCase().includes(lower) ||
            item.description.toLowerCase().includes(lower) ||
            item.domain.name.toLowerCase().includes(lower) ||
            item.input_ports.some((port) => port.output_port_name.toLowerCase().includes(lower)),
    );
}

export function MyAccessPage() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { setBreadcrumbs } = useBreadcrumbs();

    const [searchTerm, setSearchTerm] = useState('');
    const [promotingId, setPromotingId] = useState<string | null>(null);
    const [revokingId, setRevokingId] = useState<string | null>(null);

    const [revokeAccess] = useRevokeEphemeralAccessMutation();
    const [promoteAccess] = usePromoteEphemeralAccessMutation();

    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <KeyOutlined /> {t('My Access')}
                    </>
                ),
            },
        ]);
    }, [setBreadcrumbs, t]);

    const { data: items = [], isFetching } = useListEphemeralAccessQuery();

    const filteredItems = useMemo(() => filterItems(items, searchTerm), [items, searchTerm]);

    const onSearch = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchTerm(e.target.value);
    }, []);

    const handlePromote = useCallback(
        async (id: string) => {
            setPromotingId(id);
            try {
                const result = await promoteAccess(id).unwrap();
                navigate(createDataProductIdPath(result.id, DataProductTabKeys.About));
            } catch {
                dispatchMessage({ content: t('Failed to promote exploration.'), type: 'error' });
            } finally {
                setPromotingId(null);
            }
        },
        [promoteAccess, navigate, t],
    );

    const handleRevoke = useCallback(
        async (id: string) => {
            setRevokingId(id);
            try {
                await revokeAccess(id).unwrap();
                dispatchMessage({ content: t('Access revoked successfully.'), type: 'success' });
            } catch {
                dispatchMessage({ content: t('Failed to revoke access.'), type: 'error' });
            } finally {
                setRevokingId(null);
            }
        },
        [revokeAccess, t],
    );

    const columns = useMemo(
        () =>
            getMyAccessTableColumns(t, {
                onPromote: handlePromote,
                onRevoke: handleRevoke,
                promotingId,
                revokingId,
            }),
        [t, handlePromote, handleRevoke, promotingId, revokingId],
    );

    const goToMarketplace = (
        <Button type="primary" icon={<ShopOutlined />} onClick={() => navigate(ApplicationPaths.Marketplace)}>
            {t('Go to Marketplace')}
        </Button>
    );

    return (
        <Flex vertical gap="small">
            <Flex justify="space-between" align="center">
                <Input.Search
                    placeholder={t('Search by name, description, domain or output port')}
                    onChange={onSearch}
                    allowClear
                    style={{ maxWidth: 400 }}
                />
            </Flex>
            <Table<EphemeralAccessResponse>
                columns={columns}
                dataSource={filteredItems}
                rowKey={(record) => record.id}
                loading={isFetching}
                size="small"
                rowHoverable
                pagination={{
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{count}} Explorations', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                }}
                locale={{
                    emptyText: (
                        <Empty
                            styles={{ image: { height: 50 } }}
                            image={<KeyOutlined style={{ fontSize: 50 }} />}
                            description={
                                <>
                                    <Paragraph style={{ marginTop: 0, opacity: 0.45 }}>
                                        {t('No active explorations')}
                                    </Paragraph>
                                    <Paragraph style={{ opacity: 0.45 }}>
                                        {t(
                                            'Start an exploration from the Marketplace by adding output ports to your cart.',
                                        )}
                                    </Paragraph>
                                    {goToMarketplace}
                                </>
                            }
                        />
                    ),
                }}
            />
        </Flex>
    );
}
