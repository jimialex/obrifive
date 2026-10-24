import { useQuery } from "@tanstack/react-query";
import type { Product } from "@/entities/product";
import { authHttp } from "@/shared/http/client";

type Envelope<T> = { data: T };
export const productKeys = { all: ["products"] as const };

export async function getProducts(): Promise<Product[]> {
  const response = await authHttp.get<Envelope<Product[]>>("/v1/products");
  return response.data.data;
}

export function useProductsQuery() {
  return useQuery({ queryKey: productKeys.all, queryFn: getProducts });
}
