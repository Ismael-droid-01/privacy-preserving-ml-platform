export interface DatasetSummary {
    dataset_id: string;
    n_samples: number;
    n_features: number;
    numeric_features: string[];
    non_numeric_features: string[];
    missing_values: Record<string, number>;
    target: string | null;
    target_valid: boolean;
    ckks_compatible: boolean;
    preview: any[];
}

export interface PreprocessResponse {
    summary: DatasetSummary;
    isValid: boolean;
    message?: string;
}

export interface PreprocessRequest {
    dataset_base64: string;
    target?: string;
}