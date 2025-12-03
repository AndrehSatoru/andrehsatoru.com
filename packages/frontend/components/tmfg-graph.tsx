"use client"

import { useMemo, useState, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboardData } from "@/lib/dashboard-data-context"

// Cores para comunidades/grupos
const COMMUNITY_COLORS = [
  "#2563eb", // azul
  "#16a34a", // verde
  "#dc2626", // vermelho
  "#9333ea", // roxo
  "#f59e0b", // âmbar
  "#06b6d4", // ciano
  "#ec4899", // rosa
  "#84cc16", // lima
]

interface Node {
  id: string
  group: number
  degree: number
  betweenness: number
  weight: number
  x?: number
  y?: number
  vx?: number
  vy?: number
}

interface Edge {
  source: string
  target: string
  correlation: number
}

// Algoritmo de layout force-directed simplificado
function forceDirectedLayout(
  nodes: Node[],
  edges: Edge[],
  width: number,
  height: number,
  iterations: number = 100
): Node[] {
  const nodeMap = new Map<string, Node>()
  
  // Inicializar posições aleatórias
  nodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / nodes.length
    const radius = Math.min(width, height) * 0.35
    nodeMap.set(node.id, {
      ...node,
      x: width / 2 + radius * Math.cos(angle),
      y: height / 2 + radius * Math.sin(angle),
      vx: 0,
      vy: 0
    })
  })
  
  const k = Math.sqrt((width * height) / nodes.length) * 0.5
  const cooling = 0.95
  let temperature = width / 10
  
  for (let iter = 0; iter < iterations; iter++) {
    // Forças de repulsão entre todos os nós
    nodes.forEach((node1) => {
      const n1 = nodeMap.get(node1.id)!
      n1.vx = 0
      n1.vy = 0
      
      nodes.forEach((node2) => {
        if (node1.id === node2.id) return
        const n2 = nodeMap.get(node2.id)!
        
        const dx = n1.x! - n2.x!
        const dy = n1.y! - n2.y!
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        
        // Força de repulsão
        const force = (k * k) / dist
        n1.vx! += (dx / dist) * force
        n1.vy! += (dy / dist) * force
      })
    })
    
    // Forças de atração nas arestas
    edges.forEach((edge) => {
      const source = nodeMap.get(edge.source)
      const target = nodeMap.get(edge.target)
      
      if (!source || !target) return
      
      const dx = target.x! - source.x!
      const dy = target.y! - source.y!
      const dist = Math.sqrt(dx * dx + dy * dy) || 1
      
      // Força de atração (mais forte para maior correlação)
      const force = (dist * dist) / k * (0.5 + edge.correlation * 0.5)
      
      source.vx! += (dx / dist) * force
      source.vy! += (dy / dist) * force
      target.vx! -= (dx / dist) * force
      target.vy! -= (dy / dist) * force
    })
    
    // Aplicar velocidades com limites
    nodes.forEach((node) => {
      const n = nodeMap.get(node.id)!
      const speed = Math.sqrt(n.vx! * n.vx! + n.vy! * n.vy!)
      
      if (speed > temperature) {
        n.vx = (n.vx! / speed) * temperature
        n.vy = (n.vy! / speed) * temperature
      }
      
      n.x = Math.max(40, Math.min(width - 40, n.x! + n.vx!))
      n.y = Math.max(40, Math.min(height - 40, n.y! + n.vy!))
    })
    
    temperature *= cooling
  }
  
  return nodes.map((node) => ({
    ...node,
    ...nodeMap.get(node.id)
  }))
}

export function TMFGGraph() {
  const { analysisResult } = useDashboardData()
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)
  const [hoveredEdge, setHoveredEdge] = useState<{ source: string; target: string } | null>(null)
  
  const graphData = useMemo(() => {
    if (!analysisResult?.results?.tmfg_graph) {
      return null
    }
    
    const tmfg = analysisResult.results.tmfg_graph
    
    if (!tmfg.nodes || tmfg.nodes.length === 0) {
      return null
    }
    
    return {
      nodes: tmfg.nodes as Node[],
      edges: tmfg.edges as Edge[],
      stats: tmfg.stats
    }
  }, [analysisResult])
  
  const layoutData = useMemo(() => {
    if (!graphData) return null
    
    const width = 600
    const height = 500
    
    const positionedNodes = forceDirectedLayout(
      graphData.nodes,
      graphData.edges,
      width,
      height,
      150
    )
    
    return {
      nodes: positionedNodes,
      edges: graphData.edges,
      stats: graphData.stats,
      width,
      height
    }
  }, [graphData])
  
  const getNodeColor = useCallback((group: number) => {
    return COMMUNITY_COLORS[group % COMMUNITY_COLORS.length]
  }, [])
  
  const getNodeSize = useCallback((node: Node) => {
    // Tamanho baseado no grau de centralidade
    const minSize = 12
    const maxSize = 30
    return minSize + node.degree * (maxSize - minSize)
  }, [])
  
  const getEdgeOpacity = useCallback((correlation: number) => {
    return 0.3 + correlation * 0.5
  }, [])
  
  const getEdgeWidth = useCallback((correlation: number) => {
    return 1 + correlation * 3
  }, [])
  
  if (!layoutData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>TMFG (Triangulated Maximally Filtered Graph)</CardTitle>
          <CardDescription>Rede de correlações significativas entre ativos (cores = clusters)</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[500px]">
          <p className="text-muted-foreground text-sm">Envie operações com pelo menos 4 ativos para visualizar o grafo TMFG</p>
        </CardContent>
      </Card>
    )
  }
  
  const { nodes, edges, stats, width, height } = layoutData
  const nodeMap = new Map(nodes.map(n => [n.id, n]))
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>TMFG (Triangulated Maximally Filtered Graph)</CardTitle>
        <CardDescription>Rede de correlações significativas entre ativos (cores = clusters)</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex justify-center items-center" style={{ height: 380 }}>
          <svg 
            viewBox={`0 0 ${width} ${height}`} 
            className="border rounded-lg bg-slate-50"
            style={{ width: '100%', maxWidth: width, height: '100%', maxHeight: height }}
          >
            {/* Arestas */}
            {edges.map((edge, i) => {
              const source = nodeMap.get(edge.source)
              const target = nodeMap.get(edge.target)
              
              if (!source || !target) return null
              
              const isHovered = hoveredEdge?.source === edge.source && hoveredEdge?.target === edge.target
              const isConnectedToHovered = hoveredNode === edge.source || hoveredNode === edge.target
              
              return (
                <line
                  key={`edge-${i}`}
                  x1={source.x}
                  y1={source.y}
                  x2={target.x}
                  y2={target.y}
                  stroke={isHovered || isConnectedToHovered ? "#1e40af" : "#6b7280"}
                  strokeWidth={isHovered ? getEdgeWidth(edge.correlation) * 1.5 : getEdgeWidth(edge.correlation)}
                  strokeOpacity={isHovered || isConnectedToHovered ? 0.9 : getEdgeOpacity(edge.correlation)}
                  className="cursor-pointer transition-all"
                  onMouseEnter={() => setHoveredEdge(edge)}
                  onMouseLeave={() => setHoveredEdge(null)}
                />
              )
            })}
            
            {/* Nós */}
            {nodes.map((node) => {
              const size = getNodeSize(node)
              const isHovered = hoveredNode === node.id
              const isConnected = edges.some(
                e => (e.source === hoveredNode && e.target === node.id) ||
                     (e.target === hoveredNode && e.source === node.id)
              )
              
              return (
                <g key={node.id}>
                  {/* Círculo do nó */}
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={isHovered ? size * 1.2 : size}
                    fill={getNodeColor(node.group)}
                    stroke={isHovered || isConnected ? "#1e40af" : "white"}
                    strokeWidth={isHovered ? 3 : 2}
                    className="cursor-pointer transition-all"
                    onMouseEnter={() => setHoveredNode(node.id)}
                    onMouseLeave={() => setHoveredNode(null)}
                  />
                  {/* Label do nó */}
                  <text
                    x={node.x}
                    y={node.y}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={10}
                    fontWeight="bold"
                    fill="white"
                    className="pointer-events-none select-none"
                  >
                    {node.id}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
        
        {/* Tooltip */}
        {hoveredNode && (
          <div className="mt-4 p-3 rounded-lg bg-muted/50 border border-border">
            <p className="font-semibold">{hoveredNode}</p>
            {(() => {
              const node = nodeMap.get(hoveredNode)
              if (!node) return null
              return (
                <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                  <div><span className="text-muted-foreground">Centralidade:</span> <span className="font-medium">{(node.degree * 100).toFixed(0)}%</span></div>
                  <div><span className="text-muted-foreground">Betweenness:</span> <span className="font-medium">{(node.betweenness * 100).toFixed(0)}%</span></div>
                  <div><span className="text-muted-foreground">Cluster:</span> <span className="font-medium" style={{ color: getNodeColor(node.group) }}>Grupo {node.group + 1}</span></div>
                  <div><span className="text-muted-foreground">Peso na carteira:</span> <span className="font-medium">{node.weight.toFixed(1)}%</span></div>
                </div>
              )
            })()}
          </div>
        )}
        
        {hoveredEdge && !hoveredNode && (
          <div className="mt-4 p-3 rounded-lg bg-muted/50 border border-border">
            <p className="font-semibold">{hoveredEdge.source} ↔ {hoveredEdge.target}</p>
            <p className="text-sm mt-1">
              <span className="text-muted-foreground">Correlação:</span>{" "}
              <span className="font-medium">{edges.find(e => e.source === hoveredEdge.source && e.target === hoveredEdge.target)?.correlation.toFixed(2)}</span>
            </p>
          </div>
        )}
        
        {/* Estatísticas */}
        <div className="mt-5 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 rounded-lg bg-muted/50 border border-border px-4 py-3">
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Ativos:</span> <span className="font-semibold">{stats.num_nodes}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Conexões:</span> <span className="font-semibold">{stats.num_edges}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Clusters:</span> <span className="font-semibold">{stats.num_communities}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Hub Central:</span> <span className="font-semibold text-primary">{stats.most_central}</span></span>
          </div>
        </div>
        
        {/* Legenda de comunidades */}
        <div className="mt-3 flex flex-wrap items-center justify-center gap-4">
          {Array.from(new Set(nodes.map(n => n.group))).sort().map((group) => (
            <div key={group} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: getNodeColor(group) }}
              />
              <span className="text-xs text-muted-foreground">Cluster {group + 1}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
