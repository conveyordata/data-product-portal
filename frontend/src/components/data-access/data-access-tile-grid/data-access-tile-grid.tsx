import { Form, Space } from 'antd';

import { AccessDataTile } from '@/components/data-access/data-access-tile/data-access-tile.component.tsx';
import { useGetEnvironmentsQuery } from '@/store/api/services/generated/configurationEnvironmentsApi.ts';
import type { CustomDropdownItemProps } from '@/types/shared';
import styles from './data-access-tile-grid.module.scss';

type Props = {
    canAccessData: boolean;
    dataPlatforms: CustomDropdownItemProps<string>[];
    onDataPlatformClick?: (environment: string, dataPlatform: string) => Promise<void>;
    onTileClick?: (dataPlatform: string) => void;
    isLoading?: boolean;
    isDisabled?: boolean;
};

type AccessDataForm = {
    environment: string;
    dataPlatform: string;
};

export function DataAccessTileGrid({
    canAccessData,
    dataPlatforms,
    onDataPlatformClick,
    isLoading,
    isDisabled,
    onTileClick,
}: Props) {
    const { data: { environments = [] } = {}, isLoading: isLoadingEnvironments } = useGetEnvironmentsQuery();
    const [accessDataForm] = Form.useForm<AccessDataForm>();

    // TODO: Backend should provide a flag for "requires_environment" instead of using hasEnvironments as proxy
    // For now, platforms with hasEnvironments=true require environment selection, hasEnvironments=false don't
    function getEnvironment(platform: CustomDropdownItemProps<string>) {
        if (!platform.hasEnvironments) {
            return [];
        }
        return environments;
    }

    return (
        <Form<AccessDataForm>
            form={accessDataForm}
            layout="vertical"
            className={styles.formContainer}
            disabled={isLoading}
        >
            <Form.Item>
                <Space wrap className={styles.radioButtonContainer}>
                    {dataPlatforms.map((dataPlatform) => (
                        <AccessDataTile<string>
                            key={dataPlatform.value}
                            dataPlatform={dataPlatform}
                            environments={getEnvironment(dataPlatform) ?? []}
                            isDisabled={isDisabled || isLoading || isLoadingEnvironments || !canAccessData}
                            isLoading={isLoading || isLoadingEnvironments}
                            onMenuItemClick={onDataPlatformClick}
                            onTileClick={onTileClick}
                        />
                    ))}
                </Space>
            </Form.Item>
        </Form>
    );
}
