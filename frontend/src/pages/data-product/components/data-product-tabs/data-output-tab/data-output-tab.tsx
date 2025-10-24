import { Col, Row } from 'antd';
import { useState } from 'react';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice';
import { DataOutputTable } from './components/data-output-table/data-output-table.component';
import { DatasetTable } from './components/dataset-table/dataset-table.component';

type Props = {
    dataProductId: string;
};

export function DataOutputTab({ dataProductId }: Props) {
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);

    const [draggedDataOutput, setDraggedDataOutput] = useState<string | null>(null);

    const handleDragStart = (dataOutputId: string) => {
        setDraggedDataOutput(dataOutputId);
    };

    const handleDragEnd = () => {
        setDraggedDataOutput(null);
    };

    return (
        <Row gutter={24}>
            <Col span={12}>
                <DatasetTable
                    datasets={dataProduct?.datasets ?? []}
                    dataProductId={dataProductId}
                    draggedDataOutputId={draggedDataOutput}
                />
            </Col>
            <Col span={12}>
                <DataOutputTable
                    dataProductId={dataProductId}
                    dataOutputs={dataProduct?.data_outputs ?? []}
                    onDragStart={handleDragStart}
                    onDragEnd={handleDragEnd}
                />
            </Col>
        </Row>
    );
}
