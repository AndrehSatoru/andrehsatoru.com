import { enviarOperacoes } from "@/lib/backend-api";
import { BodySchema } from "shared-types";

export const runtime = "nodejs";

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

    const resp = await enviarOperacoes(parsed.data);

    // Zodios returns the data directly, not a full axios response
    return new Response(JSON.stringify(resp), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  } catch (err: any) {
    console.error("Error in /api/enviar-operacoes:", err);
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
