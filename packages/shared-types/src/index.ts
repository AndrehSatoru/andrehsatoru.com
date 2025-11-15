import { z } from "zod";

export const OperacaoSchema = z.object({
  data: z.string().min(1, "data obrigatória"),
  ticker: z.string().min(1, "ticker obrigatório"),
  tipo: z.enum(["compra", "venda"], {
    required_error: "tipo deve ser 'compra' ou 'venda'",
  }),
  valor: z.number(),
});

export const BodySchema = z.object({
  valorInicial: z.number(),
  dataInicial: z.string().min(1, "dataInicial obrigatória"),
  operacoes: z.array(OperacaoSchema).nonempty("mínimo 1 operação"),
});

export * from './schemas';