import { z } from "zod";

export const ApiErrorSchema = z.object({
  message: z.string().optional(),
  error: z.string().optional(),
  status_code: z.number().optional(),
  details: z.any().optional(),
  detail: z.union([z.string(), z.array(z.any()), z.record(z.any())]).optional(),
  request_id: z.string().optional(),
});

export type ApiError = z.infer<typeof ApiErrorSchema>;
