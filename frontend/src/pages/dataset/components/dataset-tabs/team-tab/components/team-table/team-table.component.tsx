import { Flex, Table, TableColumnsType, TableProps } from 'antd';
import { useCallback, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import {
    useGetDatasetByIdQuery,
    useRemoveUserFromDatasetMutation,
} from '@/store/features/datasets/datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { UserContract } from '@/types/users';

import styles from './team-table.module.scss';
import { getDatasetTeamColumns } from './team-table-columns.tsx';

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

    const { data: remove_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__DELETE_USER,
        },
        { skip: !datasetId },
    );
    const canRemoveNew = remove_access?.allowed || false;

    const { pagination, handlePaginationChange, resetPagination } = useTablePagination({
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<UserContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    useEffect(() => {
        resetPagination();
    }, [datasetUsers, resetPagination]);

    const handleRemoveUserAccess = useCallback(
        async (userId: string) => {
            try {
                if (!dataset) return;
                await removeDatasetUser({ datasetId: dataset.id, userId }).unwrap();
                dispatchMessage({ content: t('User access to dataset has been removed'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to remove user access from dataset'), type: 'error' });
            }
        },
        [dataset, removeDatasetUser, t],
    );

    const columns: TableColumnsType<UserContract> = useMemo(() => {
        return getDatasetTeamColumns({
            t,
            onRemoveUserAccess: handleRemoveUserAccess,
            isRemovingUser: false,
            canPerformTeamActions: (userId: string) =>
                canPerformTeamActions(isCurrentDatasetOwner, userId, currentUser.id),
            canRemove: canRemoveNew,
        });
    }, [t, handleRemoveUserAccess, isCurrentDatasetOwner, currentUser.id, canRemoveNew]);

    if (!dataset) return null;

    return (
        <Flex className={styles.teamListContainer}>
            <Table<UserContract>
                loading={isFetchingDataset || isRemovingOwner}
                className={styles.teamListTable}
                columns={columns}
                dataSource={datasetUsers}
                rowKey={({ id }) => id}
                onChange={onChange}
                pagination={{
                    ...pagination,
                    position: ['topRight'],
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{total}} dataset owners', {
                            range0: range[0],
                            range1: range[1],
                            total: total,
                        }),
                    className: styles.pagination,
                }}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
