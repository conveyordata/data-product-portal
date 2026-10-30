import { AboutEditor } from '@/components/about-editor/about-editor.component.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    useGetOutputPortQuery,
    useUpdateOutputPortAboutMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';

type Props = {
    outputPortId: string;
    dataProductId: string;
};

export function AboutTab({ outputPortId, dataProductId }: Props) {
    const query = useGetOutputPortQuery({ id: outputPortId, dataProductId });
    const [updateOutputPortAbout, { isLoading: isSaving }] = useUpdateOutputPortAboutMutation();
    const { data: editAccess } = useCheckAccessQuery(
        {
            resource: outputPortId,
            action: AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES,
        },
        { skip: !outputPortId },
    );

    return (
        <AboutEditor
            source={{
                query,
                canEdit: editAccess?.allowed ?? false,
                isSaving,
                save: (about) =>
                    updateOutputPortAbout({
                        id: outputPortId,
                        dataProductId,
                        outputPortAboutUpdate: { about },
                    }).unwrap(),
            }}
        />
    );
}
