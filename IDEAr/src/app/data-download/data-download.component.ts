import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { UtilityService } from '../services/utility.service';
import { saveAs } from 'file-saver';

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
  downloadFile(fileUrl: string): void {
    this.utilityService.downloadFile(fileUrl).subscribe((blob: Blob) => {
      // Use 'saveAs' from the FileSaver library to save the file
      saveAs(blob, fileUrl); // The file will be saved with the name passed as 'fileUrl'
    });
  }
}
