export interface DatasetMetadata {
  columns: string[];
  column_types: { [key: string]: string };
  total_rows: number;
  total_columns: number;
  null_counts: { [key: string]: number };
}

export interface DatasetPreview {
  dataset_id: string;
  metadata: DatasetMetadata;
  data: any[];
  message: string;
}

export interface UploadResponse {
  dataset_id: string;
  message: string;
}

export interface TrainingResponse {
  training_time: string;
  compute_ram: string;
  encryption_ram: string;
  message: string;
}