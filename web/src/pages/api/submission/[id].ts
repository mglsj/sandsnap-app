import { actions } from 'astro:actions';
import type { APIRoute } from "astro";

export const GET: APIRoute = async ({ params, callAction }) => {
    const { data, error } = await callAction(actions.getSubmission, { id: Number(params.id) });

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