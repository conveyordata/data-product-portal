import { EditOutlined } from '@ant-design/icons';
import { Button, Card, Col, Flex, Row, Typography } from 'antd';
import { parseAsString, useQueryState } from 'nuqs';
import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DataProductForm } from '@/components/data-products/data-product-form/data-product-form.component.tsx';
import { DataProductSelectModal } from '@/pages/cart/components/data-product-select-modal.tsx';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';

const { Title, Text } = Typography;
type Props = {
    goToNextStep: () => void;
};
export const DataProductsView = ({ goToNextStep }: Props) => {
    const { t } = useTranslation();
    const [selectedDataProductId, setSelectedDataProductId] = useQueryState('selectedDataProductId', parseAsString);
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

    const { data: dataProduct } = useGetDataProductQuery(selectedDataProductId ?? '', { skip: !selectedDataProductId });

    const selectDataProductIdModal = useCallback((dataProductId: string) => {
        setIsModalOpen(false);
        setSelectedDataProductId(dataProductId);
    }, []);

    return (
        <Row gutter={32}>
            <Col span={12}>
                {/*<Button type={"primary"} >{t("Create data product")}</Button>*/}
                <Flex vertical gap={'middle'}>
                    <Title level={4}>{t('Create a new data product')}</Title>
                    <DataProductForm mode="create" />
                </Flex>
            </Col>
            {/*<Col span={4}>*/}
            {/*    <Flex vertical align={"center"}>*/}
            {/*        <Title level={2}>{t("Or")}</Title>*/}
            {/*    </Flex>*/}
            {/*</Col>*/}

            <Col span={12}>
                <Flex vertical gap={'middle'}>
                    <Title level={4}>{t('Select an existing data product')}</Title>

                    <Card size="small" extra={null}>
                        <Flex align={'center'} justify={'space-between'}>
                            <div>
                                <Title level={4}>
                                    {selectedDataProductId ? dataProduct?.name : t('No item selected')}
                                </Title>
                                <Text>{dataProduct?.description}</Text>
                            </div>
                            <Button
                                type={selectedDataProductId ? 'default' : 'primary'}
                                icon={<EditOutlined />}
                                onClick={() => setIsModalOpen(true)}
                            >
                                {selectedDataProductId ? t('Change') : t('Select Item')}
                            </Button>
                        </Flex>
                    </Card>

                    <Button
                        type={'primary'}
                        onClick={() => {
                            goToNextStep();
                        }}
                        disabled={!selectedDataProductId}
                    >
                        {t('Confirm selected product')}
                    </Button>
                    {isModalOpen && <DataProductSelectModal selectDataProductId={selectDataProductIdModal} />}
                </Flex>
            </Col>
        </Row>
    );
};
