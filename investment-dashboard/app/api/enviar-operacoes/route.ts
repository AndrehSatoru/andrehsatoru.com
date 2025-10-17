import axios from "axios";
import { z } from "zod";

export const runtime = "nodejs";

const OperacaoSchema = z.object({
  data: z.string().min(1, "data obrigatória"),
  ticker: z.string().min(1, "ticker obrigatório"),
  tipo: z.enum(["compra", "venda"], {
    required_error: "tipo deve ser 'compra' ou 'venda'",
  }),
  valor: z.number(),
});

const BodySchema = z.object({
  valorInicial: z.number(),
  dataInicial: z.string().min(1, "dataInicial obrigatória"),
  operacoes: z.array(OperacaoSchema).nonempty("mínimo 1 operação"),
});

export async function POST(req: Request) {
  try {
    const json = await req.json();
    const parsed = BodySchema.safeParse(json);

    if (!parsed.success) {
      return new Response(
        JSON.stringify({
          message: "Corpo da requisição inválido",
          errors: parsed.error.flatten(),
        }),
        { status: 400, headers: { "content-type": "application/json" } }
      );
    }

    const url = process.env.ANDREHSATORU_URL || "https://andrehsatoru.com";

    const { valorInicial, dataInicial, operacoes } = parsed.data;

    const payload = {
      valorInicial,
      dataInicial,
      operacoes: operacoes.map((op) => ({
        data: op.data,
        ticker: op.ticker,
        tipo: op.tipo,
        valor: op.valor,
      })),
    };

    const resp = await axios.post(url, payload, {
      headers: { "content-type": "application/json" },
      // timeout: 10000,
    });

    return new Response(JSON.stringify(resp.data), {
      status: resp.status,
      headers: { "content-type": "application/json" },
    });
  } catch (err: any) {
    if (err?.response) {
      return new Response(
        JSON.stringify({
          message: "Erro na chamada externa",
          status: err.response.status,
          data: err.response.data,
        }),
        {
          status: 502,
          headers: { "content-type": "application/json" },
        }
      );
    }

    return new Response(
      JSON.stringify({ message: "Erro interno", error: String(err?.message || err) }),
      { status: 500, headers: { "content-type": "application/json" } }
    );
  }
}
