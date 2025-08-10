import type { APIRoute } from "astro";

export const GET: APIRoute = async () => {
  const programs = await import("@/assets/data/programs.json");
  const categories = await import("@/assets/data/categories.json");
  const tags = await import("@/assets/data/tags.json");
  const metadata = await import("@/assets/data/metadata.json");
  const special = await import("@/assets/data/special-configs.json");
  return new Response(
    JSON.stringify(
      {
        programs: programs.default || programs,
        categories,
        tags,
        metadata,
        special,
      },
      null,
      2
    ),
    {
      headers: { "Content-Type": "application/json" },
    }
  );
};
