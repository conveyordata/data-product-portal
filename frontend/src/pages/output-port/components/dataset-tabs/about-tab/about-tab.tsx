import { Empty } from 'antd';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    useGetOutputPortQuery,
    useUpdateOutputPortAboutMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { dispatchMessage } from '@/utils/feedback.ts';

type Props = {
    datasetId: string;
    dataProductId: string;
};

export function AboutTab({ datasetId, dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: dataset, isFetching } = useGetOutputPortQuery({ id: datasetId, dataProductId });
    const currentUser = useSelector(selectCurrentUser);
    const [updateDatasetAbout, { isLoading }] = useUpdateOutputPortAboutMutation();

    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES,
        },
        { skip: !datasetId },
    );
    const canEdit = edit_access?.allowed || false;

    if (isFetching) {
        return <LoadingSpinner />;
    }

    if (!dataset || !currentUser) {
        return <Empty />;
    }

    // Rethrowing keeps the editor open on failure, so the author does not lose their text.
    async function handleSubmit(content: string) {
        if (!canEdit) {
            dispatchMessage({ content: t('You do not have permission to edit this about section'), type: 'error' });
            throw new Error('Not allowed to edit the about section');
        }
        try {
            await updateDatasetAbout({
                id: datasetId,
                dataProductId,
                outputPortAboutUpdate: { about: content },
            }).unwrap();
            dispatchMessage({ content: t('About section successfully updated'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Could not update about section'), type: 'error' });
            throw error;
        }
    }

    return (
        <TextEditor
            initialContent={dataset.about}
            onSubmit={handleSubmit}
            isLoading={isFetching}
            isSubmitting={isLoading}
            isDisabled={!canEdit}
        />
    );
}
