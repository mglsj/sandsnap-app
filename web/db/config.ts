import { column, defineDb, defineTable } from 'astro:db';

const Submission = defineTable({
  columns: {
    id: column.number({ primaryKey: true, autoIncrement: true }),
    latitude: column.number({ optional: false }),
    longitude: column.number({ optional: false }),
    image: column.text({ optional: false }),
    createdAt: column.date({ optional: false }),
    processedAt: column.date({ optional: true }),
    size: column.number({ optional: true }),
  }
})

const Processed = defineTable({
  columns: {
    id: column.number({ primaryKey: true, autoIncrement: true }),
    submissionId: column.number({ unique: true, references: () => Submission.columns.id }),
    scale: column.text({ optional: false }),
    D10: column.number({ optional: true }),
    D16: column.number({ optional: true }),
    D25: column.number({ optional: true }),
    D50: column.number({ optional: true }),
    D65: column.number({ optional: true }),
    D75: column.number({ optional: true }),
    D90: column.number({ optional: true }),
    D50mean: column.number({ optional: true }),
  }
})

export default defineDb({
  tables: { Submission, Processed }
});
