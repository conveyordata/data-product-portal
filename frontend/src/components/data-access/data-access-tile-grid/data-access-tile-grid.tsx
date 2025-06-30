import { Form, Space } from 'antd';

import { AccessDataTile } from '@/components/data-access/data-access-tile/data-access-tile.component.tsx';
import { useGetAllEnvironmentsQuery } from '@/store/features/environments/environments-api-slice.tsx';
import { type DataPlatform, DataPlatforms } from '@/types/data-platform';
import type { CustomDropdownItemProps } from '@/types/shared';

import styles from './data-access-tile-grid.module.scss';

type Props = {
    canAccessData: boolean;
    dataPlatforms: CustomDropdownItemProps<DataPlatform>[];
    onDataPlatformClick?: (environment: string, dataPlatform: DataPlatform) => Promise<void>;
    onTileClick?: (dataPlatform: DataPlatform) => void;
    isLoading?: boolean;
    isDisabled?: boolean;
};

type AccessDataForm = {
    environment: string;
    dataPlatform: DataPlatform;
};

export function DataAccessTileGrid({
    canAccessData,
    dataPlatforms,
    onDataPlatformClick,
    isLoading,
    isDisabled,
    onTileClick,
}: Props) {
    const { data: environments, isLoading: isLoadingEnvironments } = useGetAllEnvironmentsQuery();
    const [accessDataForm] = Form.useForm<AccessDataForm>();

    function getEnvironment(platform: DataPlatform) {
        if (platform === DataPlatforms.Conveyor) {
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
                <div>
                    <Space wrap className={styles.radioButtonContainer}>
                        {dataPlatforms.map((dataPlatform) => (
                            <AccessDataTile<DataPlatform>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                environments={getEnvironment(dataPlatform.value) ?? []}
                                isDisabled={isDisabled || isLoading || isLoadingEnvironments || !canAccessData}
                                isLoading={isLoading || isLoadingEnvironments}
                                onMenuItemClick={onDataPlatformClick}
                                onTileClick={getEnvironment(dataPlatform.value) === undefined ? onTileClick : undefined}
                            />
                        ))}
                    </Space>
                </div>
            </Form.Item>
        </Form>
    );
}
