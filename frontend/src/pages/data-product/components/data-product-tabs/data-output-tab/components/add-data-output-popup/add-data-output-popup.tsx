import { Button, Form, List, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import {
    useGetDataProductByIdQuery,
    useRequestDataOutputAccessForDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { DataOutputsGetContract } from '@/types/data-output';
import { useCallback, useMemo } from 'react';
import { SearchForm } from '@/types/shared';
import { useGetAllDataOutputsQuery } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { DataOutput } from '@/types/data-output';
import { DataProductDataOutputLinkPopup } from '@/components/data-products/data-product-data-output-link-popup/data-product-data-output-link-popup.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
//import data-outputBorderIcon from '@/assets/icons/data-output-border-icon.svg?react';
import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TFunction } from 'i18next';
import styles from './add-data-output-popup.module.scss';
import { RestrictedDataOutputTitle } from '@/components/data-outputs/restricted-data-output-title/restricted-data-output-title.tsx';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    dataProductId: string;
};

const filterOutAlreadyAddedDataOutputs = (data-outputs: DataOutputsGetContract, dataProductDataOutputs: DataOutputLink[]) => {
    return (
        data-outputs.filter(
            (data-output) => !dataProductDataOutputs?.some((data-outputLink) => data-outputLink.data-output_id === data-output.id),
        ) ?? []
    );
};

const handleDataOutputListFilter = (data-outputs: DataOutputsGetContract, searchTerm: string) => {
    return data-outputs.filter((data-output) => {
        return data-output?.name?.toLowerCase().includes(searchTerm.toLowerCase());
    });
};

const getIsRestrictedDataOutput = (data-output: DataOutputsGetContract[0]) => {
    return data-output?.access_type === 'restricted';
};

const getActionButtonText = (isRestricted: boolean, t: TFunction) => {
    return isRestricted ? t('Request Access') : t('Add DataOutput');
};

export function AddDataOutputPopup({ onClose, isOpen, dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const { data: allDataOutputs = [], isFetching: isFetchingDataOutputs } = useGetAllDataOutputsQuery();
    const [requestDataOutputAccessForDataProduct, { isLoading: isRequestingAccess }] =
        useRequestDataOutputAccessForDataProductMutation();
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredDataOutputs = useMemo(() => {
        const data-outputLinks = dataProduct?.data-output_links ?? [];

        const unlinkedDataOutputs = filterOutAlreadyAddedDataOutputs(allDataOutputs, data-outputLinks);
        return searchTerm ? handleDataOutputListFilter(unlinkedDataOutputs, searchTerm) : unlinkedDataOutputs;
    }, [dataProduct?.data-output_links, allDataOutputs, searchTerm]);

    const handleRequestAccessToDataOutput = useCallback(
        async (data-outputId: string, isRestrictedDataOutput?: boolean) => {
            try {
                await requestDataOutputAccessForDataProduct({ dataProductId: dataProductId, data-outputId }).unwrap();

                const content = isRestrictedDataOutput
                    ? t('DataOutput access has been requested')
                    : t('DataOutput has been added');
                dispatchMessage({ content, type: 'success' });
            } catch (error) {
                dispatchMessage({ content: t('Failed to request access to the data product'), type: 'error' });
            }
        },
        [dataProductId, t, requestDataOutputAccessForDataProduct],
    );
    return (
        <DataProductDataOutputLinkPopup
            onClose={onClose}
            isOpen={isOpen}
            searchForm={searchForm}
            title={t('Add DataOutput')}
            searchPlaceholder={t('Search data-outputs by name')}
        >
            <List
                loading={isFetchingDataOutputs || isRequestingAccess}
                size={'large'}
                locale={{ emptyText: t('No data-outputs found') }}
                rowKey={({ id }) => id}
                dataSource={filteredDataOutputs}
                renderItem={(item) => {
                    const icon = <CustomSvgIconLoader iconComponent={data-outputBorderIcon} />;
                    const isRestrictedDataOutput = getIsRestrictedDataOutput(item);
                    const actionButtonText = getActionButtonText(isRestrictedDataOutput, t);
                    return (
                        <List.Item key={item.id}>
                            <TableCellAvatar
                                icon={icon}
                                title={
                                    isRestrictedDataOutput ? (
                                        <RestrictedDataOutputTitle name={item.name} hasPopover />
                                    ) : (
                                        item.name
                                    )
                                }
                                subtitle={
                                    <Typography.Link className={styles.noCursorPointer}>
                                        {item.business_area.name}
                                    </Typography.Link>
                                }
                            />
                            <Button
                                disabled={isRequestingAccess}
                                loading={isRequestingAccess}
                                type={'link'}
                                onClick={() => handleRequestAccessToDataOutput(item.id, isRestrictedDataOutput)}
                            >
                                {actionButtonText}
                            </Button>
                        </List.Item>
                    );
                }}
            />
        </DataProductDataOutputLinkPopup>
    );
}
