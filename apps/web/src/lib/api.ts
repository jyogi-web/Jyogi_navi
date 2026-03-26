/**
 * Backend APIクライアント設定
 * @hey-api/openapi-ts で生成されたクライアントのbaseUrlを設定する
 */
import { client } from "@jyogi-navi/openapi/client";

client.setConfig({
  baseUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080",
});

export { client };
