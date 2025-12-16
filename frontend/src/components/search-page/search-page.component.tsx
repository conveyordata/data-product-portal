import { Col, Flex, type GetProps, Input, Row, Typography } from 'antd';
import type { ReactNode } from 'react';

type SearchProps = GetProps<typeof Input.Search>;

type Props = {
    title: string;
    children: ReactNode;
    onSearch: SearchProps['onSearch'];
    searchPlaceholder: string;
    createButton?: ReactNode;
    actions?: ReactNode;
    datasetSearchFetching?: boolean;
};

export default function SearchPage({
    title,
    children,
    onSearch,
    createButton,
    searchPlaceholder,
    actions,
    datasetSearchFetching,
}: Props) {
    return (
        <Flex vertical>
            <Typography.Title level={3}>{title}</Typography.Title>
            <Row gutter={[16, 24]} align={'middle'}>
                <Col span={10}>
                    <Input.Search
                        placeholder={searchPlaceholder}
                        allowClear
                        onChange={(e) => onSearch?.(e.target.value, undefined, undefined)}
                        loading={datasetSearchFetching}
                    />
                </Col>
                <Col span={8}>{actions}</Col>
                <Col span={4} offset={2}>
                    <Flex justify="flex-end">{createButton}</Flex>
                </Col>
                <Col span={24}>{children}</Col>
            </Row>
        </Flex>
    );
}
