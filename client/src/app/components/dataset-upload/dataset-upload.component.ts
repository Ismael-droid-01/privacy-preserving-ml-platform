import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DatasetService } from '../../core/services/dataset.service';
import { DatasetPreview, UploadResponse } from '../../core/models/dataset.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dataset-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dataset-upload.component.html',
  styleUrl: './dataset-upload.component.css',
})
export class DatasetUploadComponent {
  private cdr = inject(ChangeDetectorRef);
  private datasetService = inject(DatasetService);
  private router = inject(Router);

  public selectedFile: File | null = null;
  public datasetId: string | null = null;
  public datasetPreview: DatasetPreview | null = null;
  public isUploading = false;

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
    }
  }

  onUpload() {
    if (!this.selectedFile) return;

    this.isUploading = true;

    this.datasetService.uploadDataset(this.selectedFile).subscribe({
      next: (response: UploadResponse) => {
        this.datasetId = response.dataset_id;
        this.isUploading = false;
        this.loadPreview(this.datasetId);
      },
      error: (err) => {
        this.isUploading = false;
        console.error(err)
      }
    })
  }

  loadPreview(id: string) {
    this.datasetService.getPreview(id).subscribe({
      next: (preview) => {
        this.datasetPreview = preview;
        this.cdr.detectChanges();
      }, 
      error: (err) => console.error(err)
    })
  }
  
  goToTraining() {
    if (this.datasetId) {
      this.router.navigate(['datasets/secure-train', this.datasetId]);
    }
  }

  preserveOrder = (a: any, b: any) => 0;
  /*
  errorMessage: string = '';
  isLoading: boolean = false;

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0] ?? null;
    this.errorMessage = '';
  }

  async uploadFile(): Promise<void> {
    if (!this.selectedFile) return;

    this.isLoading = true;
    this.errorMessage = '';
  
    try {
      const base64 = await this.fileToBase64(this.selectedFile);

      this.preprocessService.uploadDataset({
        dataset_base64: base64
      }).subscribe({
        next: (response) => {
          this.isLoading = false;
          if (response.dataset_id) {
            this.datasetId = response.dataset_id;
            console.log("ID guardado: ", this.datasetId);
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

  // Devuelve 0 para evitar que Angular reordene las columnas del dataset
    */
}
