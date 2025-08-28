import { BaseEdge, type EdgeProps, getSimpleBezierPath, Position } from '@xyflow/react';

export function DefaultEdge({ id, sourceX, sourceY, targetX, targetY, style }: EdgeProps) {
    const [edgePath] = getSimpleBezierPath({
        sourceX,
        sourceY,
        sourcePosition: Position.Right,
        targetX,
        targetY,
        targetPosition: Position.Left,
    });

    return <BaseEdge id={id} path={edgePath} style={style} />;
}
