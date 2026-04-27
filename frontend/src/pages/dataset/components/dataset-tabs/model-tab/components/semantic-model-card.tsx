import { Card, Tag } from 'antd';
import type {
    SemanticModelFormat,
    SemanticModelResponse,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

const FORMAT_COLORS: Record<SemanticModelFormat, string> = {
    MetricsFlow: 'blue',
    OpenSemanticInterchange: 'green',
};

type Props = {
    model: SemanticModelResponse;
};

export function SemanticModelCard({ model }: Props) {
    return (
        <Card
            size="small"
            title={
                <span>
                    {model.name} <Tag color={FORMAT_COLORS[model.format]}>{model.format}</Tag>
                </span>
            }
            style={{ marginBottom: 8 }}
        >
            <pre
                style={{
                    background: 'var(--ant-color-fill-quaternary)',
                    borderRadius: 4,
                    padding: 12,
                    overflow: 'auto',
                    maxHeight: 400,
                    fontSize: 12,
                    margin: 0,
                }}
            >
                {JSON.stringify(model.content, null, 2)}
            </pre>
        </Card>
    );
}
