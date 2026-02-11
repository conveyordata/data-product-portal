import { Button, Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { Searchbar } from '@/components/form';
import { InputPortTable } from '@/pages/data-product/components/data-product-tabs/input-port-tab/components/input-port-table/input-port-table.component.tsx';
import { type InputPort, useGetDataProductInputPortsQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { ApplicationPaths } from '@/types/navigation.ts';
import type { SearchForm } from '@/types/shared';
import styles from './input-port-tab.module.scss';

type Props = {
    dataProductId: string;
};

function filterDatasets(datasetLinks: InputPort[], searchTerm: string) {
    return (
        datasetLinks.filter(
            (datasetLink) =>
                datasetLink?.input_port?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                datasetLink?.input_port?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function InputPortTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: { input_ports: inputPorts = [] } = {} } = useGetDataProductInputPortsQuery(dataProductId);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

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
        <Flex vertical className={`${filteredDatasets.length === 0 && styles.paginationGap}`}>
            <Searchbar
                placeholder={t('Search existing Output Ports by name')}
                formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                form={searchForm}
                actionButton={
                    <Link to={ApplicationPaths.Datasets}>
                        <Button disabled={!canCreateDataset} type={'primary'}>
                            {t('Shop for new Output Ports')}
                        </Button>
                    </Link>
                }
            />
            <InputPortTable dataProductId={dataProductId} inputPorts={filteredDatasets} />
        </Flex>
    );
}
