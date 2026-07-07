import { Card, Form, List, theme } from 'antd';
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
                title={t('Note the access duration for the output ports requested:')}
                style={{ backgroundColor: token.colorInfoBg, borderColor: token.colorInfoBorder }}
            >
                <List
                    split={false}
                    size="small"
                    dataSource={cartOutputPorts}
                    renderItem={(cartOutputPort) => (
                        <List.Item key={cartOutputPort.id} style={{ padding: '2px' }}>
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
