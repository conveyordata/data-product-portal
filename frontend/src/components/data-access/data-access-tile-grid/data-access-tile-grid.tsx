import { Form, Space } from 'antd';

import { AccessDataTile } from '@/components/data-access/data-access-tile/data-access-tile.component.tsx';
import { useGetDomainQuery } from '@/store/api/services/generated/configurationDomainsApi.ts';
import { useGetEnvironmentsQuery } from '@/store/api/services/generated/configurationEnvironmentsApi.ts';
import type { CustomDropdownItemProps } from '@/types/shared';
import styles from './data-access-tile-grid.module.scss';

type Props = {
    canAccessData: boolean;
    dataPlatforms: CustomDropdownItemProps<string>[];
    domainId?: string;
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
    domainId,
    onDataPlatformClick,
    isLoading,
    isDisabled,
    onTileClick,
}: Props) {
    const { data: { environments: allEnvironments = [] } = {}, isLoading: isLoadingEnvironments } =
        useGetEnvironmentsQuery();
    const { data: domain, isLoading: isLoadingDomain } = useGetDomainQuery(domainId ?? '', { skip: !domainId });
    const globalEnvironments = allEnvironments.filter((environment) => environment.is_global !== false);
    const environments = domain?.environments.length ? domain.environments : globalEnvironments;
    const [accessDataForm] = Form.useForm<AccessDataForm>();

    if (dataPlatforms.length === 0) {
        return null;
    }

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
                            isDisabled={isDisabled || !canAccessData}
                            isLoading={isLoading || isLoadingEnvironments || isLoadingDomain}
                            onMenuItemClick={onDataPlatformClick}
                            onTileClick={
                                dataPlatform.hasEnvironments
                                    ? () => {
                                          /* tileClick does nothing if tile has environments */
                                      }
                                    : onTileClick
                            }
                        />
                    ))}
                </Space>
            </Form.Item>
        </Form>
    );
}
