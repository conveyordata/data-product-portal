import { api } from "@/store/api/services/generated/outputPortsSearchApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getGraphData: build.query<GetGraphDataApiResponse, GetGraphDataApiArg>({
      query: (queryArg) => ({
        url: `/api/v2/graph`,
        params: {
          domain_nodes_enabled: queryArg.domainNodesEnabled,
          data_product_nodes_enabled: queryArg.dataProductNodesEnabled,
          output_port_nodes_enabled: queryArg.outputPortNodesEnabled,
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
  domainNodesEnabled?: boolean;
  dataProductNodesEnabled?: boolean;
  outputPortNodesEnabled?: boolean;
};
export type Edge = {
  id: string;
  source: string;
  target: string;
  animated: boolean;
  sourceHandle?: string;
  targetHandle?: string;
};
export type DataProductType = {
  id: string;
  name: string;
  description: string;
  icon_key: DataProductIconKey;
};
export type DataProduct = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  status: DataProductStatus;
  type: DataProductType;
};
export type User = {
  id: string;
  email: string;
  external_id: string;
  first_name: string;
  last_name: string;
  has_seen_tour: boolean;
  can_become_admin: boolean;
  admin_expiry?: string | null;
};
export type Role = {
  name: string;
  scope: Scope;
  description: string;
  permissions: AuthorizationAction[];
  id: string;
  prototype: Prototype;
};
export type DataProductRoleAssignment = {
  id: string;
  data_product: DataProduct;
  user: User;
  role: Role | null;
  decision: DecisionStatus;
  requested_on: string | null;
  requested_by: User | null;
  decided_on: string | null;
  decided_by: User | null;
  data_product_id: string;
  user_id: string;
  role_id: string | null;
  requested_by_id: string | null;
  decided_by_id: string | null;
};
export type Tag = {
  id: string;
  value: string;
};
export type OutputPort = {
  id: string;
  name: string;
  namespace: string;
  description: string;
  status: OutputPortStatus;
  access_type: OutputPortAccessType;
  data_product_id: string;
  tags: Tag[];
};
export type OutputPortRoleAssignment = {
  id: string;
  output_port: OutputPort;
  user: User;
  role: Role | null;
  decision: DecisionStatus;
  requested_on: string | null;
  requested_by: User | null;
  decided_on: string | null;
  decided_by: User | null;
  output_port_id: string;
  user_id: string;
  role_id: string | null;
  requested_by_id: string | null;
  decided_by_id: string | null;
};
export type NodeData = {
  id: string;
  name: string;
  link_to_id?: string | null;
  icon_key?: string | null;
  domain?: string | null;
  domain_id?: string | null;
  description?: string | null;
  assignments?: (DataProductRoleAssignment | OutputPortRoleAssignment)[] | null;
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
export enum DataProductStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
}
export enum DataProductIconKey {
  Reporting = "reporting",
  Processing = "processing",
  Exploration = "exploration",
  Ingestion = "ingestion",
  MachineLearning = "machine_learning",
  Analytics = "analytics",
  Default = "default",
}
export enum Scope {
  Dataset = "dataset",
  DataProduct = "data_product",
  Domain = "domain",
  Global = "global",
}
export enum AuthorizationAction {
  $101 = 101,
  $102 = 102,
  $103 = 103,
  $104 = 104,
  $105 = 105,
  $106 = 106,
  $107 = 107,
  $301 = 301,
  $302 = 302,
  $303 = 303,
  $304 = 304,
  $305 = 305,
  $306 = 306,
  $307 = 307,
  $308 = 308,
  $309 = 309,
  $310 = 310,
  $311 = 311,
  $312 = 312,
  $313 = 313,
  $314 = 314,
  $315 = 315,
  $401 = 401,
  $402 = 402,
  $403 = 403,
  $404 = 404,
  $405 = 405,
  $406 = 406,
  $407 = 407,
  $408 = 408,
  $409 = 409,
  $410 = 410,
  $411 = 411,
  $412 = 412,
  $413 = 413,
  $414 = 414,
}
export enum Prototype {
  $0 = 0,
  $1 = 1,
  $2 = 2,
  $3 = 3,
}
export enum DecisionStatus {
  Approved = "approved",
  Pending = "pending",
  Denied = "denied",
}
export enum OutputPortStatus {
  Pending = "pending",
  Active = "active",
  Archived = "archived",
}
export enum OutputPortAccessType {
  Public = "public",
  Restricted = "restricted",
  Private = "private",
}
export enum NodeType {
  DataProductNode = "dataProductNode",
  DataOutputNode = "dataOutputNode",
  DatasetNode = "datasetNode",
  DomainNode = "domainNode",
}
export const { useGetGraphDataQuery, useLazyGetGraphDataQuery } =
  injectedRtkApi;
