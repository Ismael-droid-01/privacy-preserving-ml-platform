import { Routes } from '@angular/router';
import { DatasetUploadComponent } from './components/dataset-upload/dataset-upload.component';
import { SecureTrainingComponent } from './components/secure-training/secure-training.component';

export const routes: Routes = [
    { path: '', redirectTo: 'datasets/upload', pathMatch: 'full' },
    { 
        path: 'datasets',  
        children: [
            {
                path: "upload",
                component: DatasetUploadComponent,
                title: "Carga y previsualización"
            },
            {
                path: "secure-train/:id",
                component: SecureTrainingComponent,
                title: "Entrenamiento seguro"
            }
        ] 
    },
    { path: '**', redirectTo: 'datasets/upload' }
];
