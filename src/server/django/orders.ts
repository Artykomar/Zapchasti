import { DjangoApiError, fetchDjangoJson } from "@/src/server/django/client";

export type PublicOrderItem = {
  part_name: string;
  article: string;
  quantity: number;
  unit_price_rub: number;
  line_total_rub: number;
};

export type PublicOrder = {
  token: string;
  status: string;
  customer_name: string;
  vehicle: string;
  currency: string;
  total_amount_rub: number;
  delivery_terms: string;
  warranty_terms: string;
  vat_label: string;
  payment_allowed: boolean;
  payment_url: string;
  items: PublicOrderItem[];
};

export const getOrderByToken = async (token: string) => {
  try {
    return await fetchDjangoJson<PublicOrder>(`/api/orders/${encodeURIComponent(token)}/`);
  } catch (error) {
    if (error instanceof DjangoApiError && error.status === 404) {
      return undefined;
    }
    throw error;
  }
};
