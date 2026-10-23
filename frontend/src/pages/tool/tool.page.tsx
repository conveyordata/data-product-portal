import { ProductOutlined } from '@ant-design/icons';
import { Flex, Tabs, Typography } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys.ts';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { useGetAllPlatformsQuery } from '@/store/api/services/generated/configurationPlatformsApi.ts';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useGetToolQuery } from '@/store/api/services/generated/dataProductsToolsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import { ConfigurationMatrix } from './components/configuration-matrix.tsx';

export function ToolPage() {
    const { t } = useTranslation();
    const { dataProductId = '', toolId = '' } = useParams();
    const { data: tool, isLoading } = useGetToolQuery({ dataProductId, id: toolId });
    const { data: dataProduct } = useGetDataProductQuery(dataProductId);
    const { data: { platforms = [] } = {} } = useGetAllPlatformsQuery();
    const { data: access } = useCheckAccessQuery({
        resource: dataProductId,
        action: AuthorizationAction.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET,
    });

    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <ProductOutlined /> {t('Product Studio')}
                    </>
                ),
                path: ApplicationPaths.Studio,
            },
            {
                title: <>{dataProduct?.name}</>,
                path: createDataProductIdPath(dataProductId, DataProductTabKeys.Tools),
            },
            { title: <>{tool?.name}</> },
        ]);
    }, [setBreadcrumbs, dataProduct, tool, dataProductId, t]);

    if (isLoading || !tool) {
        return <LoadingSpinner />;
    }

    const platform = platforms.find((p) => p.key === tool.platform_key);
    const toolType = platform?.types.find((type) => type.name === tool.tool_type);

    return (
        <Flex vertical gap="middle">
            <Typography.Title level={3}>{tool.name}</Typography.Title>
            <Typography.Text type="secondary">
                {platform?.display_name ?? tool.platform_key} · {toolType?.display_name ?? tool.tool_type}
            </Typography.Text>
            {tool.description && <Typography.Paragraph>{tool.description}</Typography.Paragraph>}
            <Tabs
                items={[
                    {
                        key: 'configuration',
                        label: t('Configuration'),
                        children: (
                            <ConfigurationMatrix
                                dataProductId={dataProductId}
                                toolId={toolId}
                                canEdit={access?.allowed ?? false}
                            />
                        ),
                    },
                ]}
            />
        </Flex>
    );
}
