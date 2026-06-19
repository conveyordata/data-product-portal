import { List } from 'antd';
import { useMemo } from 'react';
import { Link } from 'react-router';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { useGetInputPortsForOutputPortQuery } from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { createAbstractDataProductIdPath } from '@/types/navigation';
import styles from './output-port-marketplace-card.module.scss';

type Props = {
    outputPortId: string;
    dataProductId: string;
};

export function ConsumersList({ outputPortId, dataProductId }: Props) {
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
                    <Link
                        to={createAbstractDataProductIdPath(
                            inputPort.consuming_abstract_data_product_id,
                            inputPort.consuming_abstract_data_product.abstract_data_product_type,
                        )}
                        className={styles.link}
                    >
                        {inputPort.consuming_abstract_data_product.name}
                    </Link>
                </List.Item>
            )}
        />
    );
}
