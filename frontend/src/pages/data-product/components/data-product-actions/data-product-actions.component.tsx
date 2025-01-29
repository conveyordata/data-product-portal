import { Flex } from 'antd';
import styles from './data-product-actions.module.scss';
import { useTranslation } from 'react-i18next';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { useSelector } from 'react-redux';
import {
    useGetDataProductByIdQuery,
    useGetDataProductConveyorIDEUrlMutation,
    useGetDataProductSignInUrlMutation,
    useGetDataProductDatabricksWorkspaceUrlMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import {
    getCanUserAccessDataProductData,
    getDoesUserHaveAnyDataProductMembership,
} from '@/utils/data-product-user-role.helper.ts';
import { DataAccessTileGrid } from '@/components/data-access/data-access-tile-grid/data-access-tile-grid.tsx';
import { CustomDropdownItemProps } from '@/types/shared';
import awsLogo from '@/assets/icons/aws-logo.svg?react';
import s3Logo from '@/assets/icons/s3-logo.svg?react';
import glueLogo from '@/assets/icons/glue-logo.svg?react';
import conveyorLogo from '@/assets/icons/conveyor-logo.svg?react';
import databricksLogo from '@/assets/icons/databricks-logo.svg?react';
import tableauLogo from '@/assets/icons/tableau-logo.svg?react';
import snowflakeLogo from '@/assets/icons/snowflake-logo.svg?react';
import { useMemo } from 'react';
import { TFunction } from 'i18next';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { DataPlatforms, DataPlatform } from '@/types/data-platform';
import { DataProductRequestAccessButton } from '@/pages/data-product/components/data-product-request-access-button/data-product-request-access-button.tsx';

type Props = {
    dataProductId: string;
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
        label: t('Snowflake'),
        value: DataPlatforms.Snowflake,
        icon: snowflakeLogo,
        disabled: false,
        hasConfig: true,
        children: [],
    },
    {
        label: t('Databricks'),
        value: DataPlatforms.Databricks,
        icon: databricksLogo,
        hasConfig: true,
        hasMenu: true,
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

export function DataProductActions({ dataProductId }: Props) {
    const { t } = useTranslation();
    const user = useSelector(selectCurrentUser);
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const dataPlatforms = useMemo(() => getDataPlatforms(t), [t]);
    const [getDataProductSignInUrl, { isLoading }] = useGetDataProductSignInUrlMutation();
    const [getConveyorUrl, { isLoading: isConveyorLoading }] = useGetDataProductConveyorIDEUrlMutation();
    const [getDatabricksWorkspaceUrl, { isLoading: isDatabricksLoading }] =
        useGetDataProductDatabricksWorkspaceUrlMutation();

    if (!dataProduct || !user) return null;

    const doesUserHaveAnyDataProductMembership = getDoesUserHaveAnyDataProductMembership(
        user?.id,
        dataProduct?.memberships,
    );
    const canAccessDataProductData = getCanUserAccessDataProductData(user?.id, dataProduct?.memberships);

    async function handleAccessToData(environment: string, dataPlatform: DataPlatform) {
        switch (dataPlatform) {
            case DataPlatforms.AWS:
                try {
                    const signInUrl = await getDataProductSignInUrl({ id: dataProductId, environment }).unwrap();
                    if (signInUrl) {
                        window.open(signInUrl, '_blank');
                    } else {
                        dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
                    }
                } catch (_error) {
                    dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
                }
                break;
            case DataPlatforms.Databricks:
                try {
                    const signInUrl = await getDatabricksWorkspaceUrl({ id: dataProductId, environment }).unwrap();
                    if (signInUrl) {
                        window.open(signInUrl, '_blank');
                    } else {
                        dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
                    }
                } catch (_error) {
                    dispatchMessage({ content: t('Failed to get sign in url'), type: 'error' });
                }
                break;
            default:
                break;
        }
    }

    async function handleTileClick(dataPlatform: DataPlatform) {
        switch (dataPlatform) {
            case DataPlatforms.Conveyor:
                try {
                    const url = await getConveyorUrl({ id: dataProductId }).unwrap();
                    if (url) {
                        window.open(url, '_blank');
                    } else {
                        dispatchMessage({
                            type: 'error',
                            content: t('Failed to get Conveyor url'),
                        });
                    }
                } catch (_error) {
                    dispatchMessage({
                        type: 'error',
                        content: t('Failed to get Conveyor url'),
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
                {!doesUserHaveAnyDataProductMembership && (
                    <DataProductRequestAccessButton dataProductId={dataProductId} userId={user.id} />
                )}
                <Flex vertical className={styles.accessDataContainer}>
                    <DataAccessTileGrid
                        canAccessData={canAccessDataProductData}
                        dataPlatforms={dataPlatforms}
                        onDataPlatformClick={handleAccessToData}
                        onTileClick={handleTileClick}
                        isDisabled={isLoading || !canAccessDataProductData}
                        isLoading={isLoading || isConveyorLoading || isDatabricksLoading}
                    />
                </Flex>
            </Flex>
        </>
    );
}
