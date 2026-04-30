import { Button, Flex, Input } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { InputPortTable } from '@/components/abstract-data-products/input-port-tab/components/input-port-table/input-port-table.component.tsx';
import type { InputPort } from '@/store/api/services/generated/dataProductsApi.ts';
import { ApplicationPaths } from '@/types/navigation.ts';

type Props = {
    canRequestAccess: boolean;
    canRemoveAccess: boolean;
    loadingInputPorts: boolean;
    handleRemove: (outputPortId: string) => Promise<void>;
    inputPorts: InputPort[];
};

function filterInputPorts(input_ports: InputPort[], searchTerm: string) {
    return (
        input_ports.filter(
            (input_port) =>
                input_port?.output_port?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                input_port?.output_port?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function InputPortTab({
    loadingInputPorts,
    inputPorts,
    canRequestAccess,
    handleRemove,
    canRemoveAccess,
}: Props) {
    const { t } = useTranslation();
    const [searchTerm, setSearchTerm] = useState<string>('');
    const filteredDatasets = useMemo(() => {
        return filterInputPorts(inputPorts, searchTerm);
    }, [inputPorts, searchTerm]);

    return (
        <Flex vertical gap={'middle'}>
            <Flex gap={'small'}>
                <Input.Search
                    placeholder={t('Filter by name')}
                    allowClear
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
                <Link to={ApplicationPaths.Marketplace}>
                    <Button disabled={!canRequestAccess} type={'primary'}>
                        {t('Shop for new data')}
                    </Button>
                </Link>
            </Flex>
            <InputPortTable
                loadingInputPorts={loadingInputPorts}
                inputPorts={filteredDatasets}
                handleRemove={handleRemove}
                canRemoveAccess={canRemoveAccess}
            />
        </Flex>
    );
}
