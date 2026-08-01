"use client";

import { LockKeyhole } from "lucide-react";
import { useActionState } from "react";
import { loginAdmin, type AdminLoginState } from "@/app/admin/actions";

const initialState: AdminLoginState = {};

export default function AdminLoginForm() {
  const [state, formAction, isPending] = useActionState(loginAdmin, initialState);

  return (
    <form className="admin-login-form" action={formAction}>
      <label>
        Пароль администратора
        <input name="password" type="password" autoComplete="current-password" />
      </label>
      <button type="submit" disabled={isPending}>
        <LockKeyhole size={18} aria-hidden="true" />
        {isPending ? "Проверяем" : "Войти"}
      </button>
      {state.error ? <p className="form-note form-note--error">{state.error}</p> : null}
    </form>
  );
}
