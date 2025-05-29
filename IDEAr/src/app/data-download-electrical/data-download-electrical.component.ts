import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { UtilityService } from '../services/utility.service';
import { saveAs } from 'file-saver';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmationPopupComponent } from '../confirmation-popup/confirmation-popup.component';

@Component({
  selector: 'app-data-download-electrical',
  templateUrl: './data-download-electrical.component.html',
  styleUrl: './data-download-electrical.component.css',
})
export class DataDownloadElectricalComponent implements OnInit {
  csv_files: string[] = [];
  selectedCsvFile = '';
  importedFile: File | null = null;
  constructor(
    private utilityService: UtilityService,
    private authService: AuthService,
    private router: Router,
    public dialog: MatDialog,
  ) {}

  loadData(event: Event) {
    event.stopPropagation();
    if (this.selectedCsvFile === '') {
      return;
    }
    this.utilityService.loadFileElectrical(this.selectedCsvFile);
  }

  backupData(event: Event) {
    event.stopPropagation();
    console.log('Backup data');
    this.utilityService.backupDatabaseElectrical().subscribe({
      next: (response) => {
        // Optionally, notify the user with a success message (e.g., Toast, alert)
        this.utilityService
          .getElectricalFiles()
          .subscribe((response: string[]) => {
            this.csv_files = response;
          });
      },
      error: (error) => {
        console.error('Error during database backup:', error);
        // Optionally, notify the user with an error message
      },
    });
  }

  ngOnInit(): void {
    this.authService.getAuthLevel().subscribe((level) => {
      if (level == 0) {
        this.utilityService
          .getElectricalFiles()
          .subscribe((response: string[]) => {
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
    this.utilityService.appendFileElectrical(this.importedFile).subscribe();
    console.log('Appending file:', this.importedFile.name);
  }
  downloadFile(fileUrl: string): void {
    this.utilityService.downloadFile(fileUrl).subscribe((blob: Blob) => {
      // Use 'saveAs' from the FileSaver library to save the file
      saveAs(blob, fileUrl); // The file will be saved with the name passed as 'fileUrl'
    });
  }
  deleteBackup(fileUrl: string): void {
    this.utilityService.deleteBackup(fileUrl).subscribe({
      next: (response) => {
        // Optionally, notify the user with a success message (e.g., Toast, alert)
        this.utilityService
          .getElectricalFiles()
          .subscribe((response: string[]) => {
            this.csv_files = response;
          });
      },
      error: (error) => {
        console.error('Error during file deletion:', error);
        // Optionally, notify the user with an error message
      },
    });
  }
  check_level() {
    const level = this.authService.levelGetter().subscribe((level) => {
      if (level == 0) return true;
      else return false;
    });
  }

  confirmPopup(value: string, warning: boolean, event: any, fileURL: string) {
    const ConfirmationPopUp = this.dialog.open(ConfirmationPopupComponent);
    ConfirmationPopUp.afterOpened().subscribe(() => {
      ConfirmationPopUp.componentInstance.updatePopup(value, warning);
    });

    ConfirmationPopUp.afterClosed().subscribe((result: boolean) => {
      if (result === true && value === 'backupData') {
        this.backupData(event);
      }
      if (result === true && value === 'uploadData') {
        this.uploadFile();
      }
      if (result === true && value === 'appendData') {
        this.appendFile();
      }
      if (result === true && value === 'downloadData') {
        this.downloadFile(fileURL);
      }
      if (result === true && value === 'loadData') {
        this.loadData(event);
      }
      if (result === true && value === 'deleteBackup') {
        this.deleteBackup(fileURL);
      }
    });
  }
}
