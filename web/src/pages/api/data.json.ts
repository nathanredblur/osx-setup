import type {APIContext} from 'astro';
import {getCollection} from 'astro:content';

const apps = await getCollection('apps');

export const GET = async (context: APIContext) => {
  return new Response(JSON.stringify(apps), {
    headers: {'Content-Type': 'application/json'},
  });
};
