import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PreprocessService } from '../../core/services/preprocess.service';
import { DatasetSummary } from '../../core/models/preprocess.model';

@Component({
  selector: 'app-dataset-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dataset-upload.component.html',
  styleUrl: './dataset-upload.component.css',
})
export class DatasetUploadComponent {
  // Inyeccion moderna (sin constructor)
  private preprocessService = inject(PreprocessService);
  private cdr = inject(ChangeDetectorRef);

  selectedFile: File | null = null;
  summary: DatasetSummary | null = null;
  datasetId: string | null = null;

  errorMessage: string = '';
  isLoading: boolean = false;

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0] ?? null;
    this.errorMessage = '';
    this.summary = null;
  }

  async uploadAndProcess(): Promise<void> {
    if (!this.selectedFile) return;

    this.isLoading = true;
    this.errorMessage = '';
  
    try {
      const base64 = await this.fileToBase64(this.selectedFile);

      this.preprocessService.validateAndSummarize({
        dataset_base64: base64
      }).subscribe({
        next: (response) => {
          this.isLoading = false;
          if (response.isValid && response.summary) {
            this.summary = response.summary;
            this.datasetId = response.summary.dataset_id;
            console.log("ID guardado: ", this.datasetId);
            console.log(this.summary);
            this.cdr.detectChanges();
          } else {
            this.errorMessage = response.message || 'Error desconocido';
          }
        },
        error: (err) => {
          this.isLoading = false;
          this.errorMessage = 'Error de conexión.';
          console.error(err);
          this.cdr.detectChanges();
        }
      });
    } catch (error) {
      this.isLoading = false;
      this.errorMessage = 'Error al procesar archivo.';
    }
  }

  private fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve((reader.result as string).split(',')[1]);
      reader.onerror = error => reject(error);
    });
  }

  // Devuelve 0 para evitar que Angular reordene las columnas del dataset
  preserveOrder = (a: any, b: any) => {
    return 0;
  }
}
