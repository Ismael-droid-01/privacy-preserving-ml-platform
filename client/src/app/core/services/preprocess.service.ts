import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment.development';
import { PreprocessRequest, PreprocessResponse } from '../models/preprocess.model';

@Injectable({
  providedIn: 'root',
})
export class PreprocessService {
  private http = inject(HttpClient);

  private readonly baseUrl = `${environment.apiUrl}/preprocess`;

  validateAndSummarize(data: PreprocessRequest): Observable<PreprocessResponse> {
    return this.http.post<PreprocessResponse>(
      `${this.baseUrl}/validate-and-summarize`, 
      data
    );
  }
}
