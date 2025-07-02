import { Form, Space } from 'antd';

import { AccessDataTile } from '@/components/data-access/data-access-tile/data-access-tile.component.tsx';
import { useGetAllEnvironmentsQuery } from '@/store/features/environments/environments-api-slice.tsx';

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
    const { data: environments, isLoading: isLoadingEnvironments } = useGetAllEnvironmentsQuery();
    const [accessDataForm] = Form.useForm<AccessDataForm>();

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
                            <AccessDataTile<string>
                                key={dataPlatform.value}
                                dataPlatform={dataPlatform}
                                environments={environments ?? []}
                                isDisabled={isDisabled || isLoading || isLoadingEnvironments || !canAccessData}
                                isLoading={isLoading || isLoadingEnvironments}
                                onMenuItemClick={onDataPlatformClick}
                                onTileClick={!dataPlatform.hasMenu ? onTileClick : undefined}
                            />
                        ))}
                    </Space>
                </div>
            </Form.Item>
        </Form>
    );
}
