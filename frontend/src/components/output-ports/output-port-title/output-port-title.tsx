import { Flex, Popover, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { OutputPortAccessFunction, type OutputPortAccessType } from '@/store/api/services/generated/dataProductsApi.ts';
import { OutputPortAccessIcon } from '../output-port-access-icon/output-port-access-icon.tsx';

type Props = {
    name: string;
    accessType: OutputPortAccessType;
    hasIcon?: boolean;
    hasPopover?: boolean;
};

export function OutputPortTitle({ name, accessType, hasIcon = true, hasPopover = false }: Props) {
    const { t } = useTranslation();

    const title = (
        <Flex vertical align="flex-start" gap="small">
            <Typography.Text strong>{name}</Typography.Text>
            {accessType.access_function !== OutputPortAccessFunction.Unrestricted && hasIcon && (
                <OutputPortAccessIcon accessType={accessType} />
            )}
        </Flex>
    );

    if (accessType.access_function === OutputPortAccessFunction.Unrestricted) {
        return title;
    }

    return hasPopover ? (
        <Popover content={t('{{Type}} access', { Type: accessType.name })} trigger="hover">
            {title}
        </Popover>
    ) : (
        title
    );
}
