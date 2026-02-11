import { List } from 'antd';
import { useMemo } from 'react';
import { Link } from 'react-router';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { useGetInputPortsForOutputPortQuery } from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { createDataProductIdPath } from '@/types/navigation';
import styles from './dataset-marketplace-card.module.scss';

type Props = {
    outputPortId: string;
    dataProductId: string;
};

export function DatasetProductList({ outputPortId, dataProductId }: Props) {
    const { data: { input_ports: inputPorts = [] } = {} } = useGetInputPortsForOutputPortQuery({
        outputPortId: outputPortId,
        dataProductId,
    });

    const filteredProductLinks = useMemo(() => {
        return inputPorts.filter((link) => link.status === 'approved') || [];
    }, [inputPorts]);
    if (!inputPorts) return <LoadingSpinner />;
    if (filteredProductLinks.length === 0) return null;
    return (
        <List
            dataSource={filteredProductLinks}
            renderItem={(inputPort) => (
                <List.Item style={{ margin: 0 }}>
                    <Link to={createDataProductIdPath(inputPort.data_product_id)} className={styles.link}>
                        {inputPort.data_product.name}
                    </Link>
                </List.Item>
            )}
        />
    );
}
