import { z } from 'zod';
import { schemas } from 'shared-types';

export const ApiErrorSchema = schemas.ApiErrorResponse;

export type ApiError = z.infer<typeof ApiErrorSchema>;
