import { TextEditor } from '@/components/rich-text/text-editor/text-editor.tsx';
import {
    useGetDataOutputByIdQuery,
    // useUpdateDataOutputAboutMutation,
} from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { EmptyList } from '@/components/empty/empty-list/empty-list.component.tsx';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
// import { getCanUserAccessDataOutputData } from '@/utils/data-output-user-role.helper.ts';

type Props = {
    dataOutputId: string;
};

export function AboutTab({ dataOutputId }: Props) {
    const { t } = useTranslation();
    const { data: dataOutput, isFetching } = useGetDataOutputByIdQuery(dataOutputId, { skip: !dataOutputId });
    const currentUser = useSelector(selectCurrentUser);
    const [updateDataOutputAbout, { isLoading }] = useUpdateDataOutputAboutMutation();

    if (isFetching) {
        return <LoadingSpinner />;
    }

    if (!dataOutput || !currentUser) {
        return <EmptyList />;
    }

    const canEdit =
        getCanUserAccessDataOutputData(currentUser?.id, dataOutput?.memberships) || Boolean(currentUser?.is_admin);

    async function handleSubmit(content: string) {
        if (canEdit) {
            try {
                await updateDataOutputAbout({ dataOutputId: dataOutputId, about: content }).unwrap();
                dispatchMessage({ content: t('About section successfully updated'), type: 'success' });
            } catch (error) {
                dispatchMessage({ content: t('Could not update about section'), type: 'error' });
            }
        } else {
            dispatchMessage({ content: t('You do not have permission to edit this about section'), type: 'error' });
        }
    }

    return (
        <TextEditor
            initialContent={dataOutput.about}
            onSubmit={handleSubmit}
            isLoading={isFetching}
            isSubmitting={isLoading}
            isDisabled={!canEdit}
        />
    );
}
