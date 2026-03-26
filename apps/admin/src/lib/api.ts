// 型定義は apps/web/src/client/types.gen.ts の自動生成型と対応している。
// apps/admin と apps/web は別パッケージのため、共有パッケージ化は別途対応予定。
export type DailyCount = {
  day: string;
  count: number;
};

export type AdminStats = {
  daily_questions: DailyCount[];
  total_tokens: number;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function generateMockStats(): AdminStats {
  const days: DailyCount[] = [];
  for (let i = 29; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const day = d.toISOString().slice(0, 10);
    days.push({ day, count: Math.floor(Math.random() * 40) + 1 });
  }
  const total_tokens = days.reduce((sum, d) => sum + d.count * 800, 0);
  return { daily_questions: days, total_tokens };
}

export async function fetchAdminStats(): Promise<AdminStats> {
  if (process.env.NEXT_PUBLIC_USE_MOCK === "true") {
    return generateMockStats();
  }
  const res = await fetch(`${API_BASE_URL}/api/admin/stats`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch admin stats: ${res.status}`);
  }
  return res.json() as Promise<AdminStats>;
}
