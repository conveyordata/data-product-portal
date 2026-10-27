import { Empty } from 'antd';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    useGetDataProductQuery,
    useUpdateDataProductAboutMutation,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { saveAbout } from '@/utils/about.helper.ts';

type Props = {
    dataProductId: string;
};

export function AboutTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const {
        data: dataProduct,
        isLoading: isLoadingDataProduct,
        isFetching,
    } = useGetDataProductQuery(dataProductId, { skip: !dataProductId });
    const currentUser = useSelector(selectCurrentUser);
    const [updateDataProductAbout, { isLoading }] = useUpdateDataProductAboutMutation();

    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        },
        { skip: !dataProductId },
    );
    const canEdit = edit_access?.allowed ?? false;

    if (isLoadingDataProduct) {
        return <LoadingSpinner />;
    }
    if (!dataProduct || !currentUser) {
        return <Empty />;
    }

    const handleSubmit = (about: string) =>
        saveAbout(updateDataProductAbout({ id: dataProductId, dataProductAboutUpdate: { about } }).unwrap(), t);

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
