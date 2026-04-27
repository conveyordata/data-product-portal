import { Alert, Button, Flex, Input } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { InputPortTable } from '@/pages/data-product/components/data-product-tabs/input-port-tab/components/input-port-table/input-port-table.component.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { type InputPort, useGetDataProductInputPortsQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';

type Props = {
    dataProductId: string;
};

function filterDatasets(input_ports: InputPort[], searchTerm: string) {
    return (
        input_ports.filter(
            (input_port) =>
                input_port?.output_port?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                input_port?.output_port?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function InputPortTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: { input_ports: inputPorts = [] } = {} } = useGetDataProductInputPortsQuery(dataProductId);
    const [searchTerm, setSearchTerm] = useState<string>('');
    const [bannerDismissed, setBannerDismissed] = useState(false);
    const hasStaleInputPort = inputPorts.some(
        (p) => p.status === DecisionStatus.Approved && p.output_port?.freshness_status === 'stale',
    );
    const filteredDatasets = useMemo(() => {
        return filterDatasets(inputPorts, searchTerm);
    }, [inputPorts, searchTerm]);

    const { data: access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
        },
        { skip: !dataProductId },
    );

    const canCreateDataset = access?.allowed || false;

    return (
        <Flex vertical gap={'middle'}>
            {hasStaleInputPort && !bannerDismissed && (
                <Alert
                    type="warning"
                    message={t(
                        'One or more dependencies have a broken freshness SLO. Your data product may be impacted.',
                    )}
                    closable
                    onClose={() => setBannerDismissed(true)}
                    showIcon
                />
            )}
            <Flex gap={'small'}>
                <Input.Search
                    placeholder={t('Search existing Output Ports by name')}
                    allowClear
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
                <Link to={ApplicationPaths.Marketplace}>
                    <Button disabled={!canCreateDataset} type={'primary'}>
                        {t('Shop for new Output Ports')}
                    </Button>
                </Link>
            </Flex>
            <InputPortTable dataProductId={dataProductId} inputPorts={filteredDatasets} />
        </Flex>
    );
}
