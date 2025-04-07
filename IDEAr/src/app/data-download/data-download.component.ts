import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { UtilityService } from '../services/utility.service';

@Component({
  selector: 'app-data-download',
  templateUrl: './data-download.component.html',
  styleUrl: './data-download.component.css',
})
export class DataDownloadComponent implements OnInit {
  csv_files: string[] = [];
  selectedCsvFile = '';
  constructor(private utilityService: UtilityService) {}

  loadData(event: Event) {
    event.stopPropagation();
    if (this.selectedCsvFile === '') {
      return;
    }
    console.log('load');
    this.utilityService.loadFile(this.selectedCsvFile);
  }

  backupData(event: Event) {
    event.stopPropagation();
    console.log('backup');
    this.utilityService.backupDatabase();
    this.utilityService.getFiles().subscribe((response: string[]) => {
      this.csv_files = response;
    });
  }

  ngOnInit(): void {
    console.log('in data download');
    this.utilityService.getFiles().subscribe((response: string[]) => {
      this.csv_files = response;
    });
  }

  uploadFile(event: Event) {
    event.stopPropagation();
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      this.utilityService.uploadFile(file).subscribe({
        next: (res) => console.log('Upload success:', res),
        error: (err) => console.error('Upload error:', err),
      });
    }
  }
}
