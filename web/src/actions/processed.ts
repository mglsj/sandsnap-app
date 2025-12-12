import { ActionError, defineAction } from "astro:actions"
import { db, eq, Processed, Submission } from "astro:db"
import { z } from "astro:schema"

const createProcessed = defineAction({
    input: z.object({
        id: z.number(),
        scale: z.string(),
        size: z.number(),
        D10: z.number().optional(),
        D16: z.number().optional(),
        D25: z.number().optional(),
        D50: z.number().optional(),
        D65: z.number().optional(),
        D75: z.number().optional(),
        D90: z.number(),
        D50mean: z.number(),
    }),
    accept: "form",
    handler: async (input) => {
        const submissions = await db.select().from(Submission).where(eq(Submission.id, input.id));

        if (submissions.length === 0) {
            throw new ActionError({
                code: "NOT_FOUND",
                message: "Submission not found",
            })
        }

        const processed = await db.insert(Processed).values([{
            submissionId: input.id,
            scale: input.scale,
            D10: input.D10,
            D16: input.D16,
            D25: input.D25,
            D50: input.D50,
            D65: input.D65,
            D75: input.D75,
            D90: input.D90,
            D50mean: input.D50mean,
        }]);

        await db.update(Submission)
            .set({
                processedAt: new Date(),
                size: input.size,
            })
            .where(eq(Submission.id, input.id));

        return processed;
    }
})

const getProcessed = defineAction({
    input: z.object({
        id: z.number(),
    }),
    accept: "json",

    handler: async (input) => {
        const results = await db
            .select().from(Processed)
            .where(eq(Processed.submissionId, input.id,));

        if (results.length > 0) {
            return results[0];
        } else {
            throw new ActionError({
                code: "NOT_FOUND",
                message: "Processed data not found",
            })
        }
    }
})

export { createProcessed, getProcessed }