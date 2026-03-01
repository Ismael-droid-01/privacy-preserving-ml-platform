import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment.development';
import { Observable } from 'rxjs';
import { UploadResponse, DatasetPreview, TrainingResponse } from '../models/dataset.model';

@Injectable({
  providedIn: 'root',
})
export class DatasetService {
  private http = inject(HttpClient);

  private readonly baseUrl = `${environment.apiUrl}/datasets`;

  uploadDataset(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<UploadResponse>(`${this.baseUrl}/upload`, formData);
  }

  getPreview(id: string): Observable<DatasetPreview> {
    return this.http.get<DatasetPreview>(`${this.baseUrl}/${id}/preview`);
  }

  submitTraining(datasetId: string): Observable<TrainingResponse> {
    return this.http.post<TrainingResponse>(`${this.baseUrl}/${datasetId}/submit`, {});
  }
}
