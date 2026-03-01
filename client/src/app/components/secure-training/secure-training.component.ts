import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { TrainingResponse } from '../../core/models/dataset.model';
import { DatasetService } from '../../core/services/dataset.service';

@Component({
  selector: 'app-secure-training',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './secure-training.component.html',
  styleUrl: './secure-training.component.css',
})
export class SecureTrainingComponent {
  private route = inject(ActivatedRoute);
  private datasetService = inject(DatasetService);
  private cdr = inject(ChangeDetectorRef);
  
  public datasetId: string | null = null;
  public results: TrainingResponse | null = null;
  public isTraining = false;

  ngOnInit() {
    this.datasetId = this.route.snapshot.paramMap.get('id');
    if (this.datasetId) {
      this.startSecureTraining(this.datasetId);
    }
  }

  startSecureTraining(id: string) {
    this.isTraining = true;
    this.datasetService.submitTraining(id).subscribe({
      next: (data) => {
        this.results = data;
        this.isTraining = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error(err);
        this.isTraining = false;
      }
    });
  }
}
 