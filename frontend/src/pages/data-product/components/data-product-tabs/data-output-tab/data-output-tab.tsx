import { Flex } from 'antd';
import { useState } from 'react';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { DataOutputTable } from './components/data-output-table/data-output-table.component';
import { DatasetTable } from './components/dataset-table/dataset-table.component';
import styles from './data-output-tab.module.scss';

type Props = {
    dataProductId: string;
};
export function DataOutputTab({ dataProductId }: Props) {
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);

    const [isDragging, setIsDragging] = useState(false);
    const [draggedDataOutput, setDraggedDataOutput] = useState<string | null>(null);

    const handleDragStart = (dataOutputId: string) => {
        setIsDragging(true);
        console.log(dataOutputId);
        setDraggedDataOutput(dataOutputId);
    };

    const handleDragEnd = () => {
        setIsDragging(false);
        setDraggedDataOutput(null);
    };

    return (
        <Flex vertical className={styles.container}>
            <Flex>
                <DatasetTable
                    datasets={dataProduct?.datasets ?? []}
                    dataProductId={dataProductId}
                    isDragActive={isDragging}
                    draggedDataOutputId={draggedDataOutput}
                />
                <DataOutputTable
                    dataProductId={dataProductId}
                    dataOutputs={dataProduct?.data_outputs ?? []}
                    onDragStart={handleDragStart}
                    onDragEnd={handleDragEnd}
                />
            </Flex>
        </Flex>
    );
}
