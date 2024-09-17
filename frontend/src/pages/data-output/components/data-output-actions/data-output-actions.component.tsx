import { Flex } from 'antd';
import styles from './data-output-actions.module.scss';
import { useTranslation } from 'react-i18next';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useSelector } from 'react-redux';
import {
    useGetDataOutputByIdQuery,
    // useGetDataOutputConveyorIDEUrlMutation,
    // useGetDataOutputConveyorNotebookUrlMutation,
    // useGetDataOutputSignInUrlMutation,
} from '@/store/features/data-outputs/data-outputs-api-slice.ts';
// import {
//     getCanUserAccessDataOutputData,
//     getDoesUserHaveAnyDataOutputMembership,
// } from '@/utils/data-output-user-role.helper.ts';
import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { CustomDropdownItemProps } from '@/types/shared';
import awsLogo from '@/assets/icons/aws-logo.svg?react';
import s3Logo from '@/assets/icons/s3-logo.svg?react';
import glueLogo from '@/assets/icons/glue-logo.svg?react';
import conveyorLogo from '@/assets/icons/conveyor-logo.svg?react';
import databricksLogo from '@/assets/icons/databricks-logo.svg?react';
import jupyerLogo from '@/assets/icons/jupyter-logo.svg?react';
import tableauLogo from '@/assets/icons/tableau-logo.svg?react';
import snowflakeLogo from '@/assets/icons/snowflake-logo.svg?react';
import { useMemo } from 'react';
import { TFunction } from 'i18next';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { DataPlatforms, DataPlatform } from '@/types/data-platform';
// import { DataOutputRequestAccessButton } from '@/pages/data-output/components/data-output-request-access-button/data-output-request-access-button.tsx';

type Props = {
    dataOutputId: string;
};

export const getDataPlatforms = (t: TFunction): CustomDropdownItemProps<DataPlatform>[] => [
    {
        label: t('AWS'),
        value: DataPlatforms.AWS,
        icon: awsLogo,
        hasMenu: true,
        hasConfig: true,
        children: [
            {
                label: t('S3'),
                value: DataPlatforms.S3,
                icon: s3Logo,
                hasMenu: true,
                hasConfig: true,
                children: [],
            },
            {
                label: t('Glue'),
                value: DataPlatforms.Glue,
                icon: glueLogo,
                hasMenu: true,
                hasConfig: true,
                children: [],
            },
        ],
    },
    {
        label: t('Conveyor'),
        value: DataPlatforms.Conveyor,
        icon: conveyorLogo,
        hasMenu: false,
        hasConfig: false,
        children: [],
    },
    {
        label: t('Jupyter'),
        value: DataPlatforms.ConveyorNotebook,
        icon: jupyerLogo,
        hasMenu: false,
        hasConfig: false,
        children: [],
    },
    {
        label: t('Snowflake'),
        value: DataPlatforms.Snowflake,
        icon: snowflakeLogo,
        disabled: true,
        hasConfig: true,
        children: [],
    },
    {
        label: t('Databricks'),
        value: DataPlatforms.Databricks,
        icon: databricksLogo,
        disabled: true,
        hasConfig: false,
        children: [],
    },
    {
        label: t('Tableau'),
        value: DataPlatforms.Tableau,
        icon: tableauLogo,
        disabled: true,
        hasConfig: false,
        children: [],
    },
];

export function DataOutputActions({ dataOutputId }: Props) {
    const { t } = useTranslation();
    const user = useSelector(selectCurrentUser);
    const { data: dataOutput } = useGetDataOutputByIdQuery(dataOutputId);
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);
    const [getDataOutputSignInUrl, { isLoading }] = useGetDataOutputSignInUrlMutation();
    const [getConveyorUrl, { isLoading: isConveyorLoading }] = useGetDataOutputConveyorIDEUrlMutation();
    const [getConveyorNotebookUrl, { isLoading: isConveyorNotebookLoading }] =
        useGetDataOutputConveyorNotebookUrlMutation();

    if (!dataOutput || !user) return null;

    const doesUserHaveAnyDataOutputMembership = getDoesUserHaveAnyDataOutputMembership(
        user?.id,
        dataOutput?.memberships,
    );
    const canAccessDataOutputData = getCanUserAccessDataOutputData(user?.id, dataOutput?.memberships);

    async function handleAccessToData(environment: string, dataPlatform: DataPlatform) {
        if (dataPlatform === DataPlatforms.AWS) {
            try {
                const signInUrl = await getDataOutputSignInUrl({ id: dataOutputId, environment }).unwrap();
                if (signInUrl) {
                    window.open(signInUrl, '_blank');
                } else {
                    dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
                }
            } catch (error) {
                dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
            }
        }
    }

    async function handleTileClick(dataPlatform: DataPlatform) {
        switch (dataPlatform) {
            case DataPlatforms.Conveyor:
                try {
                    const url = await getConveyorUrl({ id: dataOutputId }).unwrap();
                    if (url) {
                        window.open(url, '_blank');
                    } else {
                        dispatchMessage({
                            type: 'error',
                            content: t('Failed to get Conveyor url'),
                        });
                    }
                } catch (error) {
                    dispatchMessage({
                        type: 'error',
                        content: t('Failed to get Conveyor url'),
                    });
                }
                break;
            case DataPlatforms.ConveyorNotebook:
                try {
                    const url = await getConveyorNotebookUrl({ id: dataOutputId }).unwrap();
                    if (url) {
                        window.open(url, '_blank');
                    } else {
                        dispatchMessage({
                            type: 'error',
                            content: t('Failed to get Conveyor Notebook url'),
                        });
                    }
                } catch (error) {
                    dispatchMessage({
                        type: 'error',
                        content: t('Failed to get Conveyor Notebook url'),
                    });
                }
                break;
            default:
                break;
        }
    }

    return (
        <>
            <Flex vertical className={styles.actionsContainer}>
                {!doesUserHaveAnyDataOutputMembership && (
                    <DataOutputRequestAccessButton dataOutputId={dataOutputId} userId={user.id} />
                )}
                <Flex vertical className={styles.accessDataContainer}>
                    <DataAccessTileGrid
                        canAccessData={canAccessDataOutputData}
                        dataPlatforms={dataPlatforms}
                        onDataPlatformClick={handleAccessToData}
                        onTileClick={handleTileClick}
                        isDisabled={isLoading || !canAccessDataOutputData}
                        isLoading={isLoading || isConveyorLoading || isConveyorNotebookLoading}
                    />
                </Flex>
            </Flex>
        </>
    );
}
