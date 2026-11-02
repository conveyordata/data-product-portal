import { InfoCircleOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import {
    EmptyState,
    type EmptyStateQuery,
    emptyStateQueryProps,
    isAwaitingData,
} from '@/components/empty-state/empty-state.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor.tsx';
import { dispatchMessage } from '@/utils/feedback.ts';

export type AboutSource = {
    query: EmptyStateQuery & { currentData?: { id: string; about: string | null } };
    canEdit: boolean;
    isSaving: boolean;
    save: (about: string) => Promise<unknown>;
};

type Props = {
    source: AboutSource;
};

export function AboutEditor({ source }: Props) {
    const { t } = useTranslation();
    const { query } = source;

    if (isAwaitingData(query)) {
        return <LoadingSpinner />;
    }
    if (!query.currentData) {
        return (
            <EmptyState
                icon={<InfoCircleOutlined />}
                title={t('No About available')}
                {...emptyStateQueryProps(query)}
            />
        );
    }

    async function handleSubmit(about: string) {
        try {
            await source.save(about);
        } catch (error) {
            dispatchMessage({ content: t('Could not update about section'), type: 'error' });
            throw error;
        }
        dispatchMessage({ content: t('About section successfully updated'), type: 'success' });
    }

    return (
        <TextEditor
            key={query.currentData.id}
            initialContent={query.currentData.about}
            onSubmit={handleSubmit}
            isLoading={query.isFetching}
            isSubmitting={source.isSaving}
            isDisabled={!source.canEdit}
        />
    );
}
