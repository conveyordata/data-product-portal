import { Col, Row } from 'antd';
import { useState } from 'react';
import { useGetDataProductOutputPortsQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useGetDataProductTechnicalAssetsQuery } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { OutputPortsTable } from './components/output-ports-table/output-ports-table.component.tsx';
import { TechnicalAssetsTable } from './components/technical-assets-table/technical-assets-table.component.tsx';

type Props = {
    dataProductId: string;
};

export function DataOutputTab({ dataProductId }: Props) {
    const { data: { output_ports: outputPorts = [] } = {} } = useGetDataProductOutputPortsQuery(dataProductId);
    const { data: { technical_assets: technicalAssets = [] } = {} } =
        useGetDataProductTechnicalAssetsQuery(dataProductId);

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
                <OutputPortsTable
                    outputPorts={outputPorts}
                    dataProductId={dataProductId}
                    draggedDataOutputId={draggedDataOutput}
                />
            </Col>
            <Col span={12}>
                <TechnicalAssetsTable
                    dataProductId={dataProductId}
                    technicalAssets={technicalAssets}
                    onDragStart={handleDragStart}
                    onDragEnd={handleDragEnd}
                />
            </Col>
        </Row>
    );
}
