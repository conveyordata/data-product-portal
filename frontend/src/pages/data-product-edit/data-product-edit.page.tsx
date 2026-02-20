import { Flex, Space, Typography } from 'antd';
import { useNavigate, useParams } from 'react-router';

import { DataProductForm } from '@/components/data-products/data-product-form/data-product-form.component.tsx';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import styles from './data-product-edit.module.scss';

export function DataProductEdit() {
    const { dataProductId } = useParams();
    const { data: dataProduct, isError } = useGetDataProductQuery(dataProductId || '', { skip: !dataProductId });
    const navigate = useNavigate();

    if (!dataProductId || isError) {
        navigate(ApplicationPaths.Studio, { replace: true });
        return null;
    }

    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3} className={styles.title}>
                {dataProduct?.name}
            </Typography.Title>
            <Space orientation="vertical" size="large" className={styles.container}>
                <DataProductForm dataProductId={dataProductId} mode={'edit'} />
            </Space>
        </Flex>
    );
}
