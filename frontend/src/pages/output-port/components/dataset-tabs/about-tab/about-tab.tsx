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
import { saveAbout } from '@/utils/about.helper.ts';

type Props = {
    outputPortId: string;
    dataProductId: string;
};

export function AboutTab({ outputPortId, dataProductId }: Props) {
    const { t } = useTranslation();
    const {
        data: outputPort,
        isLoading: isLoadingOutputPort,
        isFetching,
    } = useGetOutputPortQuery({ id: outputPortId, dataProductId });
    const currentUser = useSelector(selectCurrentUser);
    const [updateOutputPortAbout, { isLoading }] = useUpdateOutputPortAboutMutation();

    const { data: edit_access } = useCheckAccessQuery(
        {
            resource: outputPortId,
            action: AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES,
        },
        { skip: !outputPortId },
    );
    const canEdit = edit_access?.allowed || false;

    if (isLoadingOutputPort) {
        return <LoadingSpinner />;
    }

    if (!outputPort || !currentUser) {
        return <Empty />;
    }

    const handleSubmit = (about: string) =>
        saveAbout(
            updateOutputPortAbout({ id: outputPortId, dataProductId, outputPortAboutUpdate: { about } }).unwrap(),
            t,
        );

    return (
        <TextEditor
            initialContent={outputPort.about}
            onSubmit={handleSubmit}
            isLoading={isFetching}
            isSubmitting={isLoading}
            isDisabled={!canEdit}
        />
    );
}
