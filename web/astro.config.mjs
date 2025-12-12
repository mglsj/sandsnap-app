// @ts-check
import { defineConfig, envField } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import svelte from "@astrojs/svelte";
import db from "@astrojs/db";
import node from "@astrojs/node";

// https://astro.build/config
export default defineConfig({
	integrations: [svelte(), db()],
	adapter: node({
		mode: "standalone",
	}),
	env: {
		schema: {
			CLOUDINARY_API_KEY: envField.string({
				context: "server",
				access: "secret",
				optional: false,
			}),
			CLOUDINARY_API_SECRET: envField.string({
				context: "server",
				access: "secret",
				optional: false,
			}),
			CLOUDINARY_CLOUD_NAME: envField.string({
				context: "server",
				access: "secret",
				optional: false,
			}),
			AZURE_STORAGE_CONNECTION_STRING: envField.string({
				context: "server",
				access: "secret",
				optional: false,
			}),
			AZURE_QUEUE_NAME: envField.string({
				context: "server",
				access: "secret",
				optional: false,
			}),
		},
	},
	output: "server",
	session: undefined,
	vite: {
		plugins: [tailwindcss()],
	},
});
