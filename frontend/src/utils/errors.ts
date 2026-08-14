import axios from "axios";

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((item) => item.msg ?? "Erro de validacao").join(", ");
    }
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Nao foi possivel concluir a operacao.";
}
