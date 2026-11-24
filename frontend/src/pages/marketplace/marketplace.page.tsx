import { ShopOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Alert, Col, Flex, Input, Pagination, Row, Typography, theme } from 'antd';
import { parseAsString, useQueryState } from 'nuqs';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { EmptyState, emptyStateQueryProps } from '@/components/empty-state/empty-state.component.tsx';
import { DataProductOutlined } from '@/components/icons';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { PosthogEvents } from '@/constants/posthog.constants';
import { SearchSuggestions } from '@/pages/marketplace/search-suggestions.tsx';
import { useGridColumnCount } from '@/pages/marketplace/use-grid-column-count.tsx';
import { useMarketplacePagination } from '@/pages/marketplace/use-marketplace-pagination.tsx';
import { useSearchDataProductsQuery } from '@/store/api/services/generated/dataProductsSearchApi.ts';
import { DataProductMarketplaceCard } from './data-product-marketplace-card/data-product-marketplace-card.component';

const CARD_MIN_WIDTH = 360;
const ROWS_PER_PAGE = 3;
const FALLBACK_COLUMNS = 4;

export function Marketplace() {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const posthog = usePostHog();
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <ShopOutlined /> {t('Marketplace')}
                    </>
                ),
            },
        ]);
    }, [setBreadcrumbs, t]);

    const searchSuggestions = useMemo(
        () => [
            t('How much money did we make this month?'),
            t('Which product is our best-seller this year?'),
            t('Who are our top biggest customers?'),
            t('Are we running low on any inventory items?'),
            t('Are we on track to hit our goals this year?'),
            t('What was our most popular ad last year?'),
            t('Are we GDPR compliant?'),
            t('What is our customer retention rate?'),
            t('Which product gets the most returns?'),
            t('What are the top things customers are complaining about?'),
            t('How many of our customer orders are currently delayed?'),
            t('Do we have a forecast of our company expenses for next month?'),
            t('What is currently sitting in our warehouse?'),
        ],
        [t],
    );

    const [searchTerm, setSearchTerm] = useQueryState('search', parseAsString.withDefault(''));
    const [searchInput, setSearchInput] = useState(searchTerm);
    useEffect(() => setSearchInput(searchTerm), [searchTerm]);

    const effectiveSearch = searchTerm.length >= 3 ? searchTerm : undefined;
    const dataProductsQuery = useSearchDataProductsQuery({ query: effectiveSearch });
    const { currentData: { data_products: dataProducts = [] } = {}, isFetching } = dataProductsQuery;

    const { ref: gridRef, columns } = useGridColumnCount(CARD_MIN_WIDTH, token.padding, FALLBACK_COLUMNS);
    const pageSize = columns * ROWS_PER_PAGE;
    const { page, setPage, pageItems } = useMarketplacePagination(
        dataProducts,
        pageSize,
        dataProductsQuery.currentData !== undefined,
    );

    const clearSearch = () => {
        setSearchTerm(null);
        setPage(1);
    };

    useEffect(() => {
        if (searchTerm?.length < 3) return;
        posthog.capture(PosthogEvents.MARKETPLACE_SEARCHED_DATA_PRODUCT, {
            search_term: searchTerm,
        });
    }, [posthog, searchTerm]);
    return (
        <Row gutter={[16, 16]}>
            <Col span={24}>
                <Typography.Title level={3}>{t('Marketplace')}</Typography.Title>
            </Col>
            <Col span={10}>
                <Input.Search
                    data-cy="marketplace-search"
                    placeholder={t('Ask a business question to find the relevant data')}
                    allowClear
                    onSearch={(e) => {
                        setSearchTerm(e);
                        setPage(1);
                    }}
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    loading={isFetching}
                />
            </Col>
            <Col span={14} />
            <Col span={10}>
                {searchSuggestions && !searchTerm && <SearchSuggestions suggestions={searchSuggestions} />}
            </Col>
            <Col span={14} />
            <Col span={24}>
                <div
                    style={{
                        background: token.colorBgLayout,
                        padding: token.padding,
                        borderRadius: token.borderRadiusLG,
                    }}
                >
                    {searchTerm && searchTerm.length < 3 && (
                        <Alert
                            title={t('Search only works when providing at least 3 characters as a search term')}
                            type="warning"
                            style={{ marginBottom: token.paddingSM }}
                        />
                    )}
                    {isFetching ? (
                        <LoadingSpinner spinProps={{ style: { height: '200px' } }} />
                    ) : dataProducts.length > 0 ? (
                        // Cards use CSS subgrid on these rows so their sections align across each visual row
                        <div
                            ref={gridRef}
                            style={{
                                display: 'grid',
                                gridTemplateColumns: `repeat(auto-fill, minmax(${CARD_MIN_WIDTH}px, 1fr))`,
                                gap: token.padding,
                            }}
                        >
                            {pageItems.map((dataProduct) => (
                                <DataProductMarketplaceCard key={dataProduct.id} dataProduct={dataProduct} />
                            ))}
                        </div>
                    ) : (
                        <EmptyState
                            icon={<DataProductOutlined />}
                            title={t('No Data Products published yet')}
                            description={t(
                                'Data Products shared with the organisation show up here, ready to request.',
                            )}
                            subject={t('Data Products')}
                            filter={{ searchTerm: effectiveSearch, onClear: clearSearch }}
                            {...emptyStateQueryProps(dataProductsQuery)}
                        />
                    )}

                    {!isFetching && dataProducts.length > pageSize && (
                        <Flex
                            key="pagination-container"
                            justify="flex-end"
                            style={{
                                marginTop: 12,
                            }}
                        >
                            <Pagination
                                current={page}
                                pageSize={pageSize}
                                total={dataProducts.length}
                                onChange={(page) => setPage(page)}
                                showSizeChanger={false} // Disable page size changer
                                showTotal={(total, range) =>
                                    t('Showing {{range0}}-{{range1}} of {{count}} Data Products', {
                                        range0: range[0],
                                        range1: range[1],
                                        count: total,
                                    })
                                }
                            />
                        </Flex>
                    )}
                </div>
            </Col>
        </Row>
    );
}
