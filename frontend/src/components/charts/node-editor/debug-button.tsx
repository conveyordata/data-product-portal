"use client"

import { Node } from '@xyflow/react';

// Even simpler version - just console logging with a button
export function SimpleDebugButton({ nodes }: { nodes: Node[] }) {
  const debugNodes = () => {
    console.log("=== NODES DEBUG ===")
    nodes.forEach((node: Node, index: number) => {
      console.log(`Node ${index + 1}:`, {
        id: node.id,
        type: node.type,
        hasType: !!node.type,
        data: node.data,
        position: node.position,
      })
    })

    // Check specifically for domain nodes
    const domainNodes = nodes.filter((node) => node.type === "domainNode")
    console.log(`Found ${domainNodes.length} domain nodes:`, domainNodes)

    // Check for nodes without types
    const noTypeNodes = nodes.filter((node) => !node.type)
    if (noTypeNodes.length > 0) {
      console.warn(`Found ${noTypeNodes.length} nodes without type:`, noTypeNodes)
    }
  }

  return (
    <button onClick={debugNodes} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
      Debug Nodes (Check Console)
    </button>
  )
}

