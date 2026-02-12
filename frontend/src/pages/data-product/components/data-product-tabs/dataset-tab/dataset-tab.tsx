import { Button, Flex, Input } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import type { DatasetLink } from '@/types/data-product';
import { ApplicationPaths } from '@/types/navigation.ts';
import { DatasetTable } from './components/dataset-table/dataset-table.component.tsx';

type Props = {
    dataProductId: string;
};

function filterDatasets(datasetLinks: DatasetLink[], searchTerm: string) {
    return (
        datasetLinks.filter(
            (datasetLink) =>
                datasetLink?.dataset?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                datasetLink?.dataset?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function DatasetTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [searchTerm, setSearchTerm] = useState<string>('');
    const filteredDatasets = useMemo(() => {
        return filterDatasets(dataProduct?.dataset_links ?? [], searchTerm);
    }, [dataProduct?.dataset_links, searchTerm]);

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
            <Flex gap={'small'}>
                <Input.Search
                    placeholder={t('Search existing Output Ports by name')}
                    allowClear
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
                <Link to={ApplicationPaths.Datasets}>
                    <Button disabled={!canCreateDataset} type={'primary'}>
                        {t('Shop for new Output Ports')}
                    </Button>
                </Link>
            </Flex>
            <DatasetTable dataProductId={dataProductId} datasets={filteredDatasets} />
        </Flex>
    );
}
