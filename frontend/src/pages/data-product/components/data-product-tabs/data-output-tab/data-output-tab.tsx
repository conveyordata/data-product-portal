import { Flex } from 'antd';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { DataOutputTable } from './components/data-output-table/data-output-table.component';
import { DatasetTable } from './components/dataset-table/dataset-table.component';
import styles from './data-output-tab.module.scss';

type Props = {
    dataProductId: string;
};
export function DataOutputTab({ dataProductId }: Props) {
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);

    return (
        <>
            <Flex vertical className={styles.container}>
                <Flex>
                    <DatasetTable datasets={dataProduct?.datasets ?? []} dataProductId={dataProductId} />
                    <DataOutputTable dataProductId={dataProductId} dataOutputs={dataProduct?.data_outputs ?? []} />
                </Flex>
            </Flex>
        </>
    );
}
