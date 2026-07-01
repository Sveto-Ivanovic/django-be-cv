export type APIResponse<T> = {
  res_status: string
  response: T;
  status?: number;
}
