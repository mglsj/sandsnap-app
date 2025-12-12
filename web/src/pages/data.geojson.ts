import { actions } from 'astro:actions';
import type { APIRoute } from "astro";
import geojson from "geojson";

export const GET: APIRoute = async ({ callAction }) => {
    const { data, error } = await callAction(actions.getAllSubmissions, {});

    if (error) {
        return new Response(
            error.message,
            {
                status: error.status,
                statusText: error.code
            },
        );
    }

    const collection = (data && data.length > 0)
        ? geojson.parse(data, { Point: ["latitude", "longitude"] })
        : { type: "FeatureCollection", features: [] };

    return new Response(JSON.stringify(collection), {
        status: 200,
        headers: {
            "Content-Type": "application/geo+json; charset=utf-8",
        },
    });
};