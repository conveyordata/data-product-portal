import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDatasetByIdQuery, useUpdateDatasetAboutMutation } from '@/store/features/datasets/datasets-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';

type Props = {
    datasetId: string;
};

export function AboutTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const { data: dataset, isFetching } = useGetDatasetByIdQuery(datasetId, { skip: !datasetId });
    const currentUser = useSelector(selectCurrentUser);
    const [updateDatasetAbout, { isLoading }] = useUpdateDatasetAboutMutation();

    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__UPDATE_PROPERTIES,
        },
        { skip: !datasetId },
    );
    const canEdit = edit_access?.allowed || false;

    if (isFetching) {
        return <LoadingSpinner />;
    }

    if (!dataset || !currentUser) {
        return <EmptyList />;
    }

    async function handleSubmit(content: string) {
        if (canEdit) {
            try {
                await updateDatasetAbout({ datasetId, about: content }).unwrap();
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
            initialContent={dataset.about}
            onSubmit={handleSubmit}
            isLoading={isFetching}
            isSubmitting={isLoading}
            isDisabled={!canEdit}
        />
    );
}
