import { Flex, Space, Typography } from 'antd';
import styles from './data-product-edit.module.scss';
import { DataProductForm } from '@/components/data-products/data-product-form/data-product-form.component.tsx';
import { useNavigate, useParams } from 'react-router-dom';
import { ApplicationPaths } from '@/types/navigation.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';

export function DataProductEdit() {
    const { dataProductId } = useParams();
    const { data: dataProduct, isError } = useGetDataProductByIdQuery(dataProductId || '', { skip: !dataProductId });
    const navigate = useNavigate();

    if (!dataProductId || isError) {
        navigate(ApplicationPaths.DataProducts, { replace: true });
        return null;
    }

    return (
        <Flex vertical className={styles.container}>
            <Typography.Title level={3} className={styles.title}>
                {dataProduct?.name}
            </Typography.Title>
            <Space direction={'vertical'} size={'large'} className={styles.container}>
                <DataProductForm dataProductId={dataProductId} mode={'edit'} />
            </Space>
        </Flex>
    );
}
