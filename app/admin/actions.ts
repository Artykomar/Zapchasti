"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import {
  clearAdminSession,
  createAdminSession,
  requireAdminSession,
  verifyAdminPassword
} from "@/src/server/auth/admin";
import { updateCustomerRequestStatus, type CustomerRequestStatus } from "@/src/server/db/catalog";

const allowedStatuses: CustomerRequestStatus[] = [
  "new",
  "in_work",
  "waiting_customer",
  "done",
  "cancelled"
];

export type AdminLoginState = {
  error?: string;
};

export async function loginAdmin(_state: AdminLoginState, formData: FormData): Promise<AdminLoginState> {
  const password = String(formData.get("password") ?? "");

  if (!verifyAdminPassword(password)) {
    return {
      error: "Неверный пароль"
    };
  }

  await createAdminSession();
  redirect("/admin");
}

export async function logoutAdmin() {
  await clearAdminSession();
  redirect("/admin/login");
}

export async function changeRequestStatus(formData: FormData) {
  await requireAdminSession();

  const requestId = String(formData.get("requestId") ?? "");
  const status = String(formData.get("status") ?? "") as CustomerRequestStatus;
  const note = String(formData.get("note") ?? "").trim().slice(0, 500);

  if (!requestId || !allowedStatuses.includes(status)) {
    return;
  }

  updateCustomerRequestStatus(requestId, status, note || `Статус изменен на ${status}`);
  revalidatePath("/admin");
  revalidatePath("/admin/requests");
}
