import { z } from 'zod';
import { schemas } from '../../shared-types/src/schemas';

export const ApiErrorSchema = schemas.ApiErrorResponse;

export type ApiError = z.infer<typeof ApiErrorSchema>;
