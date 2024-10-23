import { Flex, Table, TableColumnsType } from 'antd';
import { UserContract } from '@/types/users';
import { useMemo } from 'react';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useTranslation } from 'react-i18next';
import styles from './team-table.module.scss';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { getDatasetTeamColumns } from './team-table-columns.tsx';
import {
    useGetDatasetByIdQuery,
    useRemoveUserFromDatasetMutation,
} from '@/store/features/datasets/datasets-api-slice.ts';

type Props = {
    isCurrentDatasetOwner: boolean;
    datasetId: string;
    datasetUsers: UserContract[];
};

function canPerformTeamActions(isCurrentDatasetOwner: boolean, userId: string, currentUserId: string) {
    return isCurrentDatasetOwner && userId !== currentUserId;
}

export function TeamTable({ isCurrentDatasetOwner, datasetId, datasetUsers }: Props) {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser) as UserContract;
    const { data: dataset, isLoading: isFetchingDataset } = useGetDatasetByIdQuery(datasetId);
    const [removeDatasetUser, { isLoading: isRemovingOwner }] = useRemoveUserFromDatasetMutation();

    const handleRemoveUserAccess = async (userId: string) => {
        try {
            if (!dataset) return;
            await removeDatasetUser({ datasetId: dataset.id, userId }).unwrap();
            dispatchMessage({ content: t('User access to dataset has been removed'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Failed to remove user access from dataset'), type: 'error' });
        }
    };

    const columns: TableColumnsType<UserContract> = useMemo(() => {
        return getDatasetTeamColumns({
            t,
            onRemoveUserAccess: handleRemoveUserAccess,
            isRemovingUser: false,
            canPerformTeamActions: (userId: string) =>
                canPerformTeamActions(isCurrentDatasetOwner, userId, currentUser.id),
        });
    }, [t, handleRemoveUserAccess, isCurrentDatasetOwner, currentUser.id]);

    if (!dataset) return null;

    return (
        <Flex className={styles.teamListContainer}>
            <Table<UserContract>
                loading={isFetchingDataset || isRemovingOwner}
                className={styles.teamListTable}
                columns={columns}
                dataSource={datasetUsers}
                rowKey={({ id }) => id}
                pagination={false}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
