import { QueueServiceClient } from "@azure/storage-queue";
import type { QueueClient } from "@azure/storage-queue";
import { AZURE_STORAGE_CONNECTION_STRING, AZURE_QUEUE_NAME } from "astro:env/server";

let queueClient: QueueClient | null = null;

async function initQueueClient() {
    if (queueClient) return queueClient;

    const queueServiceClient = QueueServiceClient.fromConnectionString(AZURE_STORAGE_CONNECTION_STRING);
    queueClient = queueServiceClient.getQueueClient(AZURE_QUEUE_NAME);
    await queueClient.createIfNotExists();

    return queueClient;
}

async function enqueueMessage(message: string) {
    const client = await initQueueClient();
    return client.sendMessage(message, { messageTimeToLive: -1 });
}

export { enqueueMessage };