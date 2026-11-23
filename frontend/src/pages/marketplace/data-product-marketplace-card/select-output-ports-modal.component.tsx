import { ShoppingCartOutlined } from '@ant-design/icons';
import { Button, Checkbox, Flex, Modal, Select, Space, Typography, theme } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { DataProductOutlined } from '@/components/icons';
import { useAppDispatch } from '@/store';
import type { SearchDataProductsResponseItem } from '@/store/api/services/generated/dataProductsSearchApi.ts';
import {
    addOutputPortToCart,
    removeOutputPortFromCart,
    selectAccessModeForOutputPortInCart,
    selectCartOutputPorts,
} from '@/store/features/cart/cart-slice.ts';

type Props = {
    dataProduct: SearchDataProductsResponseItem;
    onClose: () => void;
};

type Selection = Record<string, { checked: boolean; accessModeId?: string }>;

export function SelectOutputPortsModal({ dataProduct, onClose }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();
    const dispatch = useAppDispatch();
    const cartOutputPorts = useSelector(selectCartOutputPorts);
    const cartEntry = (outputPortId: string) => cartOutputPorts.find((item) => item.outputPortId === outputPortId);

    const [selection, setSelection] = useState<Selection>(() =>
        Object.fromEntries(
            dataProduct.output_ports.map((port) => {
                const entry = cartEntry(port.id);
                return [
                    port.id,
                    {
                        checked: entry !== undefined || dataProduct.output_ports.length === 1,
                        accessModeId: entry?.accessModeId ?? port.access_modes[0]?.id,
                    },
                ];
            }),
        ),
    );
    const hasCartItems = dataProduct.output_ports.some((port) => cartEntry(port.id) !== undefined);
    const checkedCount = Object.values(selection).filter((item) => item.checked).length;

    const updateSelection = (outputPortId: string, update: Partial<Selection[string]>) =>
        setSelection((current) => ({ ...current, [outputPortId]: { ...current[outputPortId], ...update } }));

    const confirm = () => {
        for (const port of dataProduct.output_ports) {
            const { checked, accessModeId } = selection[port.id];
            const entry = cartEntry(port.id);
            if (checked && !entry) {
                dispatch(addOutputPortToCart({ outputPortId: port.id, accessModeId }));
            } else if (checked && entry && accessModeId && entry.accessModeId !== accessModeId) {
                dispatch(selectAccessModeForOutputPortInCart({ outputPortId: port.id, accessModeId }));
            } else if (!checked && entry) {
                dispatch(removeOutputPortFromCart({ outputPortId: port.id }));
            }
        }
        onClose();
    };

    return (
        <Modal
            open
            centered
            onCancel={onClose}
            title={
                <Space>
                    <DataProductOutlined />
                    {dataProduct.name}
                </Space>
            }
            footer={
                <Button
                    type="primary"
                    icon={<ShoppingCartOutlined />}
                    disabled={checkedCount === 0 && !hasCartItems}
                    onClick={confirm}
                >
                    {hasCartItems ? t('Update cart') : t('Add {{count}} to cart', { count: checkedCount })}
                </Button>
            }
        >
            <Flex vertical gap="small">
                <Typography.Text type="secondary">
                    {t('Select the Output Ports you need and pick an access mode for each.')}
                </Typography.Text>
                {dataProduct.output_ports.map((port) => {
                    const { checked, accessModeId } = selection[port.id];
                    return (
                        <Flex
                            key={port.id}
                            align="center"
                            gap="medium"
                            style={{
                                padding: token.paddingSM,
                                border: `${token.lineWidth}px solid ${checked ? token.colorPrimaryBorder : token.colorBorderSecondary}`,
                                borderRadius: token.borderRadiusLG,
                                background: checked ? token.colorPrimaryBg : undefined,
                            }}
                        >
                            <Checkbox
                                id={`output-port-${port.id}`}
                                checked={checked}
                                aria-label={port.name}
                                onChange={(e) => updateSelection(port.id, { checked: e.target.checked })}
                            />
                            <label
                                htmlFor={`output-port-${port.id}`}
                                style={{ flex: 1, minWidth: 0, cursor: 'pointer' }}
                            >
                                <Flex vertical>
                                    <Typography.Text strong ellipsis={{ tooltip: true }}>
                                        {port.name}
                                    </Typography.Text>
                                    <Typography.Paragraph
                                        type="secondary"
                                        ellipsis={{ rows: 2, tooltip: true }}
                                        style={{ marginBottom: 0 }}
                                    >
                                        {port.description}
                                    </Typography.Paragraph>
                                </Flex>
                            </label>
                            {port.access_modes.length > 0 && (
                                <Select
                                    aria-label={t('Access mode for {{name}}', { name: port.name })}
                                    value={accessModeId}
                                    onChange={(value) => updateSelection(port.id, { accessModeId: value })}
                                    options={port.access_modes.map((mode) => ({ value: mode.id, label: mode.name }))}
                                    style={{ minWidth: 120 }}
                                />
                            )}
                        </Flex>
                    );
                })}
            </Flex>
        </Modal>
    );
}
