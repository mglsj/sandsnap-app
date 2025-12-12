import { actions } from 'astro:actions';
import type { APIRoute } from "astro";

export const POST: APIRoute = async ({ request, callAction }) => {
    const formData = await request.formData();
    const { data, error } = await callAction(actions.createProcessed, formData);

    if (error) {
        return new Response(
            error.message,
            {
                status: error.status,
                statusText: error.code
            },
        );
    }

    return new Response(JSON.stringify(data));
};