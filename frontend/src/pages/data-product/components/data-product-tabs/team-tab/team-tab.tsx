import styles from './team-tab.module.scss';
import { Button, Flex, Form } from 'antd';
import { useTranslation } from 'react-i18next';
import { useCallback, useMemo } from 'react';
import { useModal } from '@/hooks/use-modal.tsx';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
import { getIsDataProductOwner } from '@/utils/data-product-user-role.helper.ts';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { TeamTable } from '@/pages/data-product/components/data-product-tabs/team-tab/components/team-table/team-table.component.tsx';
import { SearchForm } from '@/types/shared';
import { Searchbar } from '@/components/form';
import { DataProductMembershipRole, DataProductUserMembership } from '@/types/data-product-membership';
import { UserPopup } from '@/components/modal/user-popup/user-popup.tsx';
import { UserContract } from '@/types/users';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useAddDataProductMembershipMutation } from '@/store/features/data-product-memberships/data-product-memberships-api-slice.ts';

type Props = {
    dataProductId: string;
};

function filterUsers(users: DataProductUserMembership[], searchTerm: string) {
    if (!searchTerm) return users;
    if (!users) return [];

    return (
        users.filter(
            (membership) =>
                membership?.user?.email?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                membership?.user?.first_name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                membership?.user?.last_name?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function TeamTab({ dataProductId }: Props) {
    const { isVisible, handleOpen, handleClose } = useModal();
    const user = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    const { data: dataProduct, isFetching } = useGetDataProductByIdQuery(dataProductId);
    const [addUserToDataProduct, { isLoading: isAddingUser }] = useAddDataProductMembershipMutation();
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredUsers = useMemo(() => {
        return filterUsers(dataProduct?.memberships ?? [], searchTerm);
    }, [dataProduct?.memberships, searchTerm]);
    const dataProductUserIds = useMemo(() => filteredUsers.map((user) => user.user.id), [filteredUsers]);

    const isDataProductOwner = useMemo(() => {
        if (!dataProduct || !user) return false;

        return getIsDataProductOwner(dataProduct, user.id) || user.is_admin;
    }, [dataProduct, user]);

    const handleGrantAccessToDataProduct = useCallback(
        async (user: UserContract) => {
            try {
                await addUserToDataProduct({
                    dataProductId: dataProductId,
                    user_id: user.id,
                    role: DataProductMembershipRole.Member,
                }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the data product'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant access to the data product'), type: 'error' });
            }
        },
        [addUserToDataProduct, dataProductId, t],
    );

    if (!dataProduct || !user) return null;

    return (
        <>
            <Flex vertical className={styles.container}>
                <Searchbar
                    form={searchForm}
                    formItemProps={{ initialValue: '' }}
                    placeholder={t('Search users by email or name')}
                    actionButton={
                        <Button
                            disabled={!isDataProductOwner}
                            type={'primary'}
                            className={styles.formButton}
                            onClick={handleOpen}
                        >
                            {t('Add User')}
                        </Button>
                    }
                />
                <TeamTable
                    isCurrentUserDataProductOwner={isDataProductOwner}
                    dataProductId={dataProductId}
                    dataProductUsers={filteredUsers}
                />
            </Flex>
            {isVisible && (
                <UserPopup
                    isOpen={isVisible}
                    onClose={handleClose}
                    isLoading={isFetching || isAddingUser}
                    userIdsToHide={dataProductUserIds}
                    item={{
                        action: handleGrantAccessToDataProduct,
                        label: t('Grant Access'),
                    }}
                />
            )}
        </>
    );
}
