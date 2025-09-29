/**
 * Represents a single document summary item returned by the service.
 * Note: createDateTime is an ISO 8601 string.
 */
export interface DocumentSummary {
  author: string;
  consumerDocumentId: string;
  consumerFilename: string;
  consumerIdentifier: string;
  consumerReferenceId: string;
  createDateTime: string; // ISO 8601, e.g., 2025-09-23T22:21:44+00:00
  documentClass: string; // e.g., "MHR"
  documentServiceId: string;
  documentType: string; // e.g., "WILL"
  documentTypeDescription: string;
  documentURL: string; // signed URL
  fileSize?: string
}

/** Convenience type for the list response */
export type DocumentSummaryList = DocumentSummary[];
