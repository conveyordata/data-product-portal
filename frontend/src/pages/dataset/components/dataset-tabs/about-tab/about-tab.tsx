import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDatasetByIdQuery, useUpdateDatasetAboutMutation } from '@/store/features/datasets/datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { getIsDatasetOwner } from '@/utils/dataset-user.helper.ts';

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
    const canEditNew = edit_access?.allowed || false;

    if (isFetching) {
        return <LoadingSpinner />;
    }

    if (!dataset || !currentUser) {
        return <EmptyList />;
    }

    const canEdit = getIsDatasetOwner(dataset, currentUser?.id) || Boolean(currentUser?.is_admin);

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
            isDisabled={!(canEditNew || canEdit)}
        />
    );
}
