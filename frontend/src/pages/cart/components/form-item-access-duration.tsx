import { InfoCircleOutlined } from '@ant-design/icons';
import { Card, Flex, Form, List, theme } from 'antd';
import { useTranslation } from 'react-i18next';
import { OutputPortAccessDuration } from '@/pages/cart/components/output-port-access-duration.tsx';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import type { DataProductChoiceOptions } from '@/store/features/cart/cart-slice.ts';

type Props = {
    cartOutputPorts?: SearchOutputPortsResponseItem[];
    dataProductTypeChoice: DataProductChoiceOptions;
};

export const FormItemAccessDuration = ({ cartOutputPorts, dataProductTypeChoice }: Props) => {
    const { t } = useTranslation();
    const { token } = theme.useToken();

    return (
        <Form.Item>
            <Card
                size="small"
                title={
                    <Flex gap="small">
                        <InfoCircleOutlined style={{ color: token.colorInfo }} />
                        {t('Note the access duration for the output ports requested')}
                    </Flex>
                }
                style={{ backgroundColor: token.colorInfoBg, borderColor: token.colorInfoBorder }}
                styles={{ header: { minHeight: 32 }, body: { padding: '4px 12px' } }}
            >
                <List
                    split={false}
                    size="small"
                    dataSource={cartOutputPorts}
                    style={{ paddingLeft: 20 }}
                    renderItem={(cartOutputPort) => (
                        <List.Item
                            key={cartOutputPort.id}
                            style={{ padding: '2px 0', display: 'list-item', listStyleType: 'disc' }}
                        >
                            <OutputPortAccessDuration
                                outputPort={cartOutputPort}
                                dataProductTypeChoice={dataProductTypeChoice}
                            />
                        </List.Item>
                    )}
                />
            </Card>
        </Form.Item>
    );
};
