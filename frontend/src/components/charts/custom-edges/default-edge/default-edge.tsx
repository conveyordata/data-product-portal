import { BaseEdge, type EdgeProps, getSimpleBezierPath } from '@xyflow/react';

export function DefaultEdge({ id, sourceX, sourceY, targetX, targetY }: EdgeProps) {
    const [edgePath] = getSimpleBezierPath({
        sourceX,
        sourceY,
        targetX,
        targetY,
    });

    return <BaseEdge id={id} path={edgePath} />;
}
