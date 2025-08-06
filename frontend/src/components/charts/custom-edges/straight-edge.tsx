import { BaseEdge, type EdgeProps, getStraightPath } from '@xyflow/react';

export function StraightEdge({ id, sourceX, sourceY, targetX, targetY, style }: EdgeProps) {
    // Define a margin to stop the edge before the node boundary (hard coded... based on size of node would be better code practice)
    const margin = 35;
    
    // angle
    const angle = Math.atan2(targetY - sourceY, targetX - sourceX);
    const angleDeg = angle * (180 / Math.PI);

    // Adjust coordinates based on the margin
    const cos = margin * Math.cos(angle);
    const sin = margin * Math.sin(angle);

    const adjustedSourceX = sourceX + cos;
    const adjustedSourceY = sourceY + sin;
    
    const adjustedTargetX = targetX - cos;
    const adjustedTargetY = targetY - sin;
    
    // Midpoint for arrow
    const midX = (sourceX + targetX) / 2
    const midY = (sourceY + targetY) / 2
    

    const [edgePath] = getStraightPath({
        sourceX: adjustedSourceX,
        sourceY: adjustedSourceY,
        targetX: adjustedTargetX,
        targetY: adjustedTargetY,
    });


    return (
        <>
            <BaseEdge id={id} path={edgePath} style={style} />;
            {/* Arrow in the middle */}
            <polygon
                points="0,0 12,4 0,8 2,4"
                fill="currentColor"
                stroke="currentColor"
                strokeWidth="1"
                transform={`translate(${midX}, ${midY}) rotate(${angleDeg}) translate(-6, -4)`}
                style={{
                fill: style?.stroke || "#b1b1b7",
                stroke: style?.stroke || "#b1b1b7",
                }}
            />
        </>
    );
}
