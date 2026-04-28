import { Empty, Flex, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import {
    useGetOutputPortSemanticModelsQuery,
    useGetOutputPortTableSchemasQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { SemanticModelList } from './components/semantic-model-list';
import { TableSchemaList } from './components/table-schema-list';

type Props = {
    datasetId: string;
    dataProductId: string;
};

export function ModelTab({ datasetId, dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: tableSchemas = [], isFetching: isFetchingSchemas } = useGetOutputPortTableSchemasQuery({
        id: datasetId,
        dataProductId,
    });

    const { data: semanticModels = [], isFetching: isFetchingModels } = useGetOutputPortSemanticModelsQuery({
        id: datasetId,
        dataProductId,
    });

    if (isFetchingSchemas || isFetchingModels) {
        return <LoadingSpinner />;
    }

    return (
        <Flex vertical gap="middle">
            <div>
                <Typography.Title level={5}>{t('Tables')}</Typography.Title>
                {tableSchemas.length === 0 ? (
                    <Empty description={t('No table schemas imported yet')} />
                ) : (
                    <TableSchemaList schemas={tableSchemas} />
                )}
            </div>
            <div>
                <Typography.Title level={5}>{t('Semantic Models')}</Typography.Title>
                {semanticModels.length === 0 ? (
                    <Empty description={t('No semantic models imported yet')} />
                ) : (
                    <SemanticModelList models={semanticModels} />
                )}
            </div>
        </Flex>
    );
}
