import { Col, type GetProps, Input, Row, Typography } from 'antd';
import { type ReactNode, useState } from 'react';
import { SearchSuggestions } from '@/components/search-page/search-suggestions.tsx';

type SearchProps = GetProps<typeof Input.Search>;

type Props = {
    title: string;
    children: ReactNode;
    onChange?: SearchProps['onChange'];
    onSearch?: SearchProps['onSearch'];
    searchPlaceholder: string;
    actions?: ReactNode;
    loadingResults?: boolean;
    searchSuggestions?: string[];
};

export default function SearchPage({
    title,
    children,
    onSearch,
    onChange,
    searchPlaceholder,
    actions,
    loadingResults,
    searchSuggestions,
}: Props) {
    const [searched, setSearched] = useState<boolean>(false);
    return (
        <Row gutter={[16, 16]}>
            <Col span={24}>
                <Typography.Title level={3}>{title}</Typography.Title>
            </Col>
            <Col span={10}>
                <Input.Search
                    placeholder={searchPlaceholder}
                    allowClear
                    onChange={onChange}
                    onSearch={(e) => {
                        setSearched(true);
                        onSearch?.(e);
                    }}
                    loading={loadingResults}
                />
            </Col>
            <Col span={14}>{actions}</Col>
            <Col span={10}>
                {searchSuggestions && !searched && <SearchSuggestions suggestions={searchSuggestions} />}
            </Col>
            <Col span={24}>{children}</Col>
        </Row>
    );
}
