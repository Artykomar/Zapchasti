"use client";

export default function GlobalError({ retry }: { error: Error & { digest?: string }; retry: () => void }) {
  return (
    <html lang="ru">
      <body style={{ margin: 0, background: "#07111f", color: "#f4f8ff", fontFamily: "Arial, sans-serif" }}>
        <main style={{ maxWidth: 720, margin: "15vh auto", padding: 32, textAlign: "center" }}>
          <title>Ошибка | Zemazap</title>
          <h1>Не удалось открыть страницу</h1>
          <p>Попробуйте ещё раз. Технические детали не показываются посетителям.</p>
          <button
            type="button"
            onClick={() => retry()}
            style={{ padding: "12px 20px", borderRadius: 10, border: 0, cursor: "pointer" }}
          >
            Повторить
          </button>
        </main>
      </body>
    </html>
  );
}
