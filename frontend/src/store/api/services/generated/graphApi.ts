import { api } from "@/store/api/services/generated/outputPortsSearchApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getGraphData: build.query<GetGraphDataApiResponse, GetGraphDataApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/graph`,
        params: {
          output_port_nodes_enabled: queryArg.outputPortNodesEnabled,
          exploration_nodes_enabled: queryArg.explorationNodesEnabled,
        },
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetGraphDataApiResponse =
  /** status 200 Successful Response */ Graph;
export type GetGraphDataApiArg = {
  outputPortNodesEnabled?: boolean;
  explorationNodesEnabled?: boolean;
};
export type Edge = {
  id: string;
  source: string;
  target: string;
  animated: boolean;
  sourceHandle?: string;
  targetHandle?: string;
};
export type NodeData = {
  id: string;
  name: string;
  link_to_id?: string | null;
  icon_key?: string | null;
  domain?: string | null;
  domain_id?: string | null;
  description?: string | null;
};
export type Node = {
  id: string;
  data: NodeData;
  type: NodeType;
  isMain?: boolean;
};
export type Graph = {
  edges: Edge[];
  nodes: Node[];
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
  input?: any;
  ctx?: object;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export enum NodeType {
  DataProductNode = "dataProductNode",
  ExplorationNode = "explorationNode",
  TechnicalAssetNode = "technicalAssetNode",
  OutputPortNode = "outputPortNode",
}
export const { useGetGraphDataQuery, useLazyGetGraphDataQuery } =
  injectedRtkApi;
