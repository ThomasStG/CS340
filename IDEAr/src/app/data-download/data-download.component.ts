import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { UtilityService } from '../services/utility.service';
import { saveAs } from 'file-saver';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-data-download',
  templateUrl: './data-download.component.html',
  styleUrl: './data-download.component.css',
})
export class DataDownloadComponent implements OnInit {
  csv_files: string[] = [];
  selectedCsvFile = '';
  importedFile: File | null = null;
  constructor(
    private utilityService: UtilityService,
    private authService: AuthService,
    private router: Router,
  ) {}

  loadData(event: Event) {
    event.stopPropagation();
    if (this.selectedCsvFile === '') {
      return;
    }
    this.utilityService.loadFile(this.selectedCsvFile);
  }

  backupData(event: Event) {
    event.stopPropagation();
    this.utilityService.backupDatabase();
    this.utilityService.getFiles().subscribe((response: string[]) => {
      this.csv_files = response;
    });
  }

  ngOnInit(): void {
    this.authService.getAuthLevel().subscribe((level) => {
      if (level == 0) {
        this.utilityService.getFiles().subscribe((response: string[]) => {
          this.csv_files = response;
        });
      } else {
        this.router.navigate(['/authentication']);
      }
    });
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.importedFile = input.files[0];
      console.log('File selected:', this.importedFile.name);
    }
  }

  uploadFile() {
    if (!this.importedFile) {
      console.error('No file selected.');
      return;
    }

    const formData = new FormData();
    formData.append('file', this.importedFile);

    // send formData to your backend using HttpClient
    this.utilityService.uploadFile(this.importedFile).subscribe();
    console.log('Uploading file:', this.importedFile.name);
  }

  appendFile() {
    if (!this.importedFile) {
      console.error('No file selected.');
      return;
    }

    // Similar to uploadFile, or whatever append logic you want
    this.utilityService.appendFile(this.importedFile).subscribe();
    console.log('Appending file:', this.importedFile.name);
  }
  downloadFile(fileUrl: string): void {
    this.utilityService.downloadFile(fileUrl).subscribe((blob: Blob) => {
      // Use 'saveAs' from the FileSaver library to save the file
      saveAs(blob, fileUrl); // The file will be saved with the name passed as 'fileUrl'
    });
  }
  check_level() {
    const level = this.authService.levelGetter().subscribe((level) => {
      if (level == 0) return true;
      else return false;
    });
  }
}
