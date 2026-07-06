import { Alert, Form, List } from 'antd';
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

    return (
        <Form.Item>
            <Alert
                title={
                    <List
                        header={t('Note the access duration for the output ports requested:')}
                        dataSource={cartOutputPorts}
                        renderItem={(cartOutputPort) => {
                            return (
                                <List.Item key={cartOutputPort.id}>
                                    {' '}
                                    <OutputPortAccessDuration
                                        outputPort={cartOutputPort}
                                        dataProductTypeChoice={dataProductTypeChoice}
                                    />{' '}
                                </List.Item>
                            );
                        }}
                    />
                }
                type="info"
                showIcon
            />
        </Form.Item>
    );
};
