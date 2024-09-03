import styles from './data-product-tab.module.scss';
import { Badge, Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { useTranslation } from 'react-i18next';
import { Searchbar } from '@/components/form';
import { SearchForm } from '@/types/shared';
import { DataProductLink } from '@/types/dataset';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { DataProductTable } from '@/pages/dataset/components/dataset-tabs/data-product-tab/components/data-product-table/data-product-table.component.tsx';
import { getIsDatasetOwner } from '@/utils/dataset-user.helper.ts';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component';
import { createDataProductIdPath } from '@/types/navigation';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper';
import { getDataProductDatasetLinkBadgeStatus, getDataProductDatasetLinkStatusLabel } from '@/utils/status.helper';

type Props = {
    dataOutputId: string;
};

export function DataProductTab({ dataOutputId }: Props) {
    const { t } = useTranslation();
    const user = useSelector(selectCurrentUser);
    const { data: dataoutput, isLoading } = useGetDataOutputByIdQuery(dataOutputId);
    const data_product = useMemo(() => {
        return dataoutput?.owner || undefined;
    }, [dataoutput?.id, dataoutput?.owner]);
    const [searchForm] = Form.useForm<SearchForm>();

    // const isDatasetOwner = useMemo(() => {
    //     if (!dataset || !user) return false;

    //     return getIsDatasetOwner(dataset, user.id) || user.is_admin;
    // }, [dataset?.id, user?.id]);

    return (
        <>
            <Flex vertical className={styles.container}>
                <TableCellAvatar
                    popover={{ title: data_product?.name, content: data_product?.description }}
                    linkTo={createDataProductIdPath(data_product?.id || '')}
                    icon={
                        <CustomSvgIconLoader
                            iconComponent={getDataProductTypeIcon(data_product?.type?.icon_key)}
                            hasRoundBorder
                            size={'default'}
                        />
                    }
                    title={data_product?.name}
                    // subtitle={
                    //     // <Badge
                    //     //     status={getDataProductDatasetLinkBadgeStatus(status)}
                    //     //     text={getDataProductDatasetLinkStatusLabel(status)}
                    //     //     className={styles.noSelect}
                    //     // />
                    // }
                />
            </Flex>
            {/* Todo - Allow to initiate data-product-dataset-link action from the dataset (for restricted datasets) */}
            {/*{isVisible && <AddDataProductPopup onClose={handleClose} isOpen={isVisible} datasetId={datasetId} />}*/}
        </>
    );
}
