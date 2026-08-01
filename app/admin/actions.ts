"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import {
  clearAdminSession,
  createAdminSession,
  requireAdminSession,
  verifyAdminPassword
} from "@/src/server/auth/admin";
import {
  addCustomerRequestComment,
  importPriceRows,
  updateCustomerRequestStatus,
  updateProductActivity,
  type CustomerRequestStatus
} from "@/src/server/db/catalog";
import { parsePriceImportFile } from "@/src/server/import/priceImport";

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
  revalidatePath(`/admin/requests/${requestId}`);
}

export async function addRequestComment(formData: FormData) {
  await requireAdminSession();

  const requestId = String(formData.get("requestId") ?? "");
  const note = String(formData.get("note") ?? "");

  if (!requestId || !note.trim()) {
    return;
  }

  addCustomerRequestComment(requestId, note);
  revalidatePath("/admin");
  revalidatePath("/admin/requests");
  revalidatePath(`/admin/requests/${requestId}`);
}

export async function setProductActivity(formData: FormData) {
  await requireAdminSession();

  const partId = String(formData.get("partId") ?? "");
  const isActive = String(formData.get("isActive") ?? "") === "true";

  if (!partId) {
    return;
  }

  updateProductActivity(partId, isActive);
  revalidatePath("/admin");
  revalidatePath("/admin/products");
  revalidatePath("/catalog");
}

export async function importPriceFile(formData: FormData) {
  await requireAdminSession();

  const file = formData.get("file");

  if (!(file instanceof File) || file.size === 0) {
    redirect("/admin/products/import?result=empty");
  }

  const parsed = await parsePriceImportFile(file);
  const result = importPriceRows(parsed.filename, parsed.fileKind, parsed.rows);

  revalidatePath("/admin");
  revalidatePath("/admin/products");
  revalidatePath("/catalog");
  redirect(
    `/admin/products/import?result=ok&imported=${result.importedRows}&skipped=${result.skippedRows}`
  );
}
