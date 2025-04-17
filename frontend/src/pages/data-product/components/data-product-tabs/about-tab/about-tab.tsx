import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import {
    useGetDataProductByIdQuery,
    useUpdateDataProductAboutMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { getCanUserAccessDataProductData } from '@/utils/data-product-user-role.helper.ts';

type Props = {
    dataProductId: string;
};

export function AboutTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isFetching } = useGetDataProductByIdQuery(dataProductId, { skip: !dataProductId });
    const currentUser = useSelector(selectCurrentUser);
    const [updateDataProductAbout, { isLoading }] = useUpdateDataProductAboutMutation();
    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        },
        { skip: !dataProductId },
    );

    const canEditNew = edit_access?.allowed || false;
    if (isFetching) {
        return <LoadingSpinner />;
    }

    if (!dataProduct || !currentUser) {
        return <EmptyList />;
    }

    const canEdit =
        getCanUserAccessDataProductData(currentUser?.id, dataProduct?.memberships) || Boolean(currentUser?.is_admin);

    async function handleSubmit(content: string) {
        if (canEdit || canEditNew) {
            try {
                await updateDataProductAbout({ dataProductId: dataProductId, about: content }).unwrap();
                dispatchMessage({ content: t('About section successfully updated'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Could not update about section'), type: 'error' });
            }
        } else {
            dispatchMessage({ content: t('You do not have permission to edit this about section'), type: 'error' });
        }
    }

    return (
        <TextEditor
            initialContent={dataProduct.about}
            onSubmit={handleSubmit}
            isLoading={isFetching}
            isSubmitting={isLoading}
            isDisabled={!canEdit}
        />
    );
}
