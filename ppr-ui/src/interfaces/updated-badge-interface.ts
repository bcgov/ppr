import { BaseDataUnionIF } from "./base-data-union-interface";

export interface UpdatedBadgeIF {
  action?: string,
  baseline: BaseDataUnionIF,
  currentState: BaseDataUnionIF
}
