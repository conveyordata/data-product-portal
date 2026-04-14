import { ExperimentOutlined, GiftOutlined } from '@ant-design/icons';
import { Card, Col, Flex, Row, Typography } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { CartOverview } from '@/pages/cart/components/cart-overview.component.tsx';
import { useSearchOutputPortsQuery } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { selectCartDatasetIds } from '@/store/features/cart/cart-slice.ts';

const { Title, Text } = Typography;

export enum DataProductChoiceOptions {
    exploration = 'EXPLORATION',
    data_product = 'DATA_PRODUCT',
}
type Props = {
    selectOption: (option: DataProductChoiceOptions) => void;
};

export const DataProductChoice = ({ selectOption }: Props) => {
    const { t } = useTranslation();
    const { data: { output_ports: outputPorts = [] } = {}, isFetching: fetchingOutputPorts } =
        useSearchOutputPortsQuery({ limit: 1000 });
    const cartDatasetIds = useSelector(selectCartDatasetIds);

    const cartOutputPorts = useMemo(() => {
        if (cartDatasetIds.length === 0) {
            return [];
        }
        return outputPorts?.filter((dataset) => cartDatasetIds.includes(dataset.id));
    }, [outputPorts, cartDatasetIds]);

    return (
        <Flex vertical gap={'middle'}>
            <Title level={2}>{t('How will you use this data?')}</Title>
            <Text>{t('Choose the option that best describes your needs')}</Text>
            <Row gutter={[16, 32]}>
                <Col span={12}>
                    <Card
                        hoverable
                        onClick={() => {
                            selectOption(DataProductChoiceOptions.exploration);
                        }}
                    >
                        <Card.Meta
                            avatar={<ExperimentOutlined style={{ fontSize: '40px' }} />}
                            title={t('I want to explore this data')}
                            description={t('I need a one-time answer or personal sandbox')}
                        />
                    </Card>
                </Col>
                <Col span={12}>
                    <Card
                        hoverable
                        onClick={() => {
                            selectOption(DataProductChoiceOptions.data_product);
                        }}
                    >
                        <Card.Meta
                            avatar={<GiftOutlined style={{ fontSize: '40px' }} />}
                            title={t('I want to build data products')}
                            description={t('I want to transform, govern and share data with others')}
                        />
                    </Card>
                </Col>
                <Col span={24}>
                    <CartOverview loading={fetchingOutputPorts} cartOutputPorts={cartOutputPorts} />
                </Col>
            </Row>
        </Flex>
    );
};
