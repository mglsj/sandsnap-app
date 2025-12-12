import { ActionError, defineAction } from "astro:actions"
import { db, eq, Submission } from "astro:db"
import { z } from "astro:schema"
import { uploadStream } from "../lib/images";
import { enqueueMessage } from "../lib/queue";

const createSubmission = defineAction({
    input: z.object({
        longitude: z.number(),
        latitude: z.number(),
        image: z.custom<File>((val) => val instanceof File),
    }),
    accept: "form",
    handler: async (input) => {
        if (input.image.type !== "image/jpeg" && input.image.type !== "image/jpg" && input.image.type !== "image/png") {
            throw new ActionError({
                code: "BAD_REQUEST",
                message: "Invalid image type. Only JPEG and PNG are allowed.",
            })
        }

        const arrayBuffer = await input.image.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);

        let response;

        try {
            response = await uploadStream(uint8Array, {
                folder: "sand",
                resource_type: "image",
            })
        } catch (error) {
            throw new ActionError({
                code: "INTERNAL_SERVER_ERROR",
                message: "Image upload to cloudinary failed",
            })
        } finally {
            if (!response || !response.secure_url) {
                throw new ActionError({
                    code: "INTERNAL_SERVER_ERROR",
                    message: "Image upload to cloudinary failed",
                })
            }
        }



        const results = await db
            .insert(Submission)
            .values([{
                image: response.secure_url,
                longitude: input.longitude,
                latitude: input.latitude,
                createdAt: new Date(),
            }])
            .returning();

        if (results.length === 0) {
            throw new ActionError({
                code: "INTERNAL_SERVER_ERROR",
                message: "Failed to create submission",
            })
        }

        await enqueueMessage(`${results[0].id},${response.secure_url}`);

        return results[0];
    }
})

const getSubmission = defineAction({
    input: z.object({
        id: z.number(),
    }),
    accept: "json",

    handler: async (input) => {
        const results = await db
            .select().from(Submission)
            .where(eq(Submission.id, input.id,));

        if (results.length > 0) {
            return results[0];
        } else {
            throw new ActionError({
                code: "NOT_FOUND",
                message: "Submission not found",
            })
        }
    }
})

const getAllSubmissions = defineAction({
    input: z.object({}),
    accept: "json",
    handler: async () => {
        const results = await db
            .select().from(Submission)

        return results;
    }
})

export { createSubmission, getSubmission, getAllSubmissions }

