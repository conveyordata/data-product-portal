import { ColumnContract } from "./column.contract";
import { ServiceLevelObjectiveContract } from "./service-level-objective.contract";

export interface DataContractContract {
    id: string;
    table: string;
    description: string;
    checks: string[];
    quality_score: number;
    columns: ColumnContract[];
    service_level_objectives: ServiceLevelObjectiveContract[];
}
