import { Alert, Button, Card, Col, Flex, Modal, Row, Spin } from 'antd';
import { useTranslation } from 'react-i18next';
import { AccessModesField } from '@/components/access-modes/access-modes-field.component';
import { useGetOutputPortQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { useGetTechnicalAssetQuery } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';

type Props = {
    onClose: () => void;
    dataProductId: string;
    outputPortId: string;
    technicalAssetId: string;
};

export function IncompatibleAccessModesModal({ onClose, dataProductId, outputPortId, technicalAssetId }: Props) {
    const { t } = useTranslation();
    const {
        data: outputPort,
        isLoading: isLoadingOutputPort,
        isError: isOutputPortError,
    } = useGetOutputPortQuery({ dataProductId, id: outputPortId });
    const {
        data: technicalAsset,
        isLoading: isLoadingTechnicalAsset,
        isError: isTechnicalAssetError,
    } = useGetTechnicalAssetQuery({
        id: technicalAssetId,
        dataProductId,
    });

    const isLoading = isLoadingOutputPort || isLoadingTechnicalAsset;
    const hasError = isOutputPortError || isTechnicalAssetError || !outputPort || !technicalAsset;

    return (
        <Modal
            title={t('Incompatible access modes')}
            open
            onCancel={onClose}
            width={900}
            footer={[
                <Button key="close" onClick={onClose}>
                    {t('Close')}
                </Button>,
            ]}
        >
            {isLoading ? (
                <Spin size="large" />
            ) : hasError ? (
                <Alert
                    showIcon
                    type="error"
                    title={t('Failed to load access mode details')}
                    description={t('The incompatible access mode details could not be loaded.')}
                />
            ) : (
                <Flex gap="middle" vertical>
                    <Alert
                        showIcon
                        type="error"
                        title={t(
                            'The access modes configured on the Output Port and Technical Asset are incompatible.',
                        )}
                        description={t('To fix it create a new Technical Asset with compatible access modes.')}
                    />
                    <Row gutter={16}>
                        <Col span={12}>
                            <Card size="small" title={`${t('Output Port')}: ${outputPort.name}`}>
                                <AccessModesField accessModes={outputPort.access_modes} />
                            </Card>
                        </Col>
                        <Col span={12}>
                            <Card size="small" title={`${t('Technical Asset')}: ${technicalAsset.name}`}>
                                <AccessModesField accessModes={technicalAsset.access_modes} />
                            </Card>
                        </Col>
                    </Row>
                </Flex>
            )}
        </Modal>
    );
}
