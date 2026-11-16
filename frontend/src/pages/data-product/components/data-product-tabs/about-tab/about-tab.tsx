import { AboutEditor } from '@/components/about-editor/about-editor.component.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    useGetDataProductQuery,
    useUpdateDataProductAboutMutation,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';

type Props = {
    dataProductId: string;
};

export function AboutTab({ dataProductId }: Props) {
    const query = useGetDataProductQuery(dataProductId, { skip: !dataProductId });
    const [updateDataProductAbout, { isLoading: isSaving }] = useUpdateDataProductAboutMutation();
    const { data: editAccess } = useCheckAccessQuery(
        {
            resource: dataProductId,
            action: AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        },
        { skip: !dataProductId },
    );

    return (
        <AboutEditor
            source={{
                query,
                canEdit: editAccess?.allowed ?? false,
                isSaving,
                save: (about) =>
                    updateDataProductAbout({ id: dataProductId, dataProductAboutUpdate: { about } }).unwrap(),
            }}
        />
    );
}
