import { Modal, Table } from 'antd';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useGetDataProductsQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import type { DataProduct } from '@/store/api/services/generated/usersApi.ts';

type Props = {
    selectDataProductId: (dataProductId: string) => void;
};
export const DataProductSelectModal = ({ selectDataProductId }: Props) => {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser);
    const { data: { data_products: userDataProducts = [] } = {}, isFetching: isFetchingUserDataProducts } =
        useGetDataProductsQuery(currentUser?.id, {
            skip: currentUser === null || !currentUser?.id,
        });
    return (
        <Modal open title={t('Select a data product')} width={800} cancelButtonProps={{}}>
            <Table<DataProduct>
                dataSource={userDataProducts}
                loading={isFetchingUserDataProducts}
                onRow={(record, _) => {
                    return {
                        onClick: (_) => {
                            selectDataProductId(record.id);
                        }, // click row
                    };
                }}
                columns={[
                    {
                        title: t('Name'),
                        dataIndex: 'name',
                    },
                ]}
            />
        </Modal>
    );
};
