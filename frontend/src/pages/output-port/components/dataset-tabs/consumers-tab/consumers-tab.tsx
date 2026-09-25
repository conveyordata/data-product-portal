import { UserAddOutlined } from '@ant-design/icons';
import { Button, Flex, Input, Tooltip } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type OutputPortInputPort,
    useGetInputPortsForOutputPortQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { ConsumersTable } from './components/consumers-table/consumers-table.component';
import { GrantOutputPortAccessModal } from './components/grant-output-port-access-modal.tsx';

type Props = {
    outputPortId: string;
    dataProductId: string;
};

function filterDataProducts(dataProductLinks: OutputPortInputPort[], searchTerm: string) {
    return (
        dataProductLinks.filter((item) =>
            item?.consuming_abstract_data_product.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function ConsumersTab({ outputPortId, dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: { input_ports: inputPorts = [] } = {}, isLoading } = useGetInputPortsForOutputPortQuery({
        outputPortId: outputPortId,
        dataProductId,
    });
    const [searchTerm, setSearchTerm] = useState<string>('');
    const [isGrantModalOpen, setIsGrantModalOpen] = useState(false);
    const { data: approveAccess } = useCheckAccessQuery({
        resource: outputPortId,
        action: AuthorizationAction.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
    });
    const filteredDataProducts = useMemo(() => {
        return filterDataProducts(inputPorts, searchTerm);
    }, [inputPorts, searchTerm]);

    return (
        <Flex vertical gap="middle">
            <Flex gap="middle">
                <Input.Search
                    placeholder={t('Search consumers by name')}
                    allowClear
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
                {approveAccess?.allowed && (
                    <Tooltip title="You can use this to directly add a new consumer to this Output Port, this is the only way to add consumers to private Output Ports.">
                        <Button type="primary" icon={<UserAddOutlined />} onClick={() => setIsGrantModalOpen(true)}>
                            {t('Add consumer')}
                        </Button>
                    </Tooltip>
                )}
            </Flex>
            <ConsumersTable
                outputPortId={outputPortId}
                dataProductId={dataProductId}
                dataProducts={filteredDataProducts}
                isLoading={isLoading}
            />
            {isGrantModalOpen && (
                <GrantOutputPortAccessModal
                    dataProductId={dataProductId}
                    outputPortId={outputPortId}
                    existingConsumerIds={inputPorts.map(
                        ({ consuming_abstract_data_product_id }) => consuming_abstract_data_product_id,
                    )}
                    onClose={() => setIsGrantModalOpen(false)}
                />
            )}
        </Flex>
    );
}
