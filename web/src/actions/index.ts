import { createProcessed, getProcessed } from './processed';
import { createSubmission, getAllSubmissions, getSubmission } from './submission';

export const server = { createSubmission, getSubmission, createProcessed, getProcessed, getAllSubmissions };