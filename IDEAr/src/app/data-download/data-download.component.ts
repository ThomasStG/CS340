import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { UtilityService } from '../services/utility.service';
import { saveAs } from 'file-saver';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmationPopupComponent } from '../confirmation-popup/confirmation-popup.component';

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
    public dialog: MatDialog,
  ) {}

  loadData(event: Event) {
    event.stopPropagation();
    if (this.selectedCsvFile === '') {
      return;
    }
    this.utilityService.loadFile(this.selectedCsvFile);
  } // Load data from the selected CSV file
  // Args: event: Event - The event that triggered the load data action
  // Returns: void

  backupData(event: Event) {
    event.stopPropagation();
    this.utilityService.backupDatabase();
    this.utilityService.getFiles().subscribe((response: string[]) => {
      this.csv_files = response;
    });
  } // Backup the database
  // Args: event: Event - The event that triggered the backup data action
  // Returns: void

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
  } // Initialize the component (data download)
  // Args: None
  // Returns: void

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.importedFile = input.files[0];
      console.log('File selected:', this.importedFile.name);
    }
  } // Handle file selection
  // Args: event: Event - The event that triggered the file selection
  // Returns: void

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
  } // Upload the selected file
  // Args: None
  // Returns: void

  appendFile() {
    if (!this.importedFile) {
      console.error('No file selected.');
      return;
    }

    // Similar to uploadFile, or whatever append logic you want
    this.utilityService.appendFile(this.importedFile).subscribe();
    console.log('Appending file:', this.importedFile.name);
  } // Append the selected file
  // Args: None
  // Returns: void

  downloadFile(fileUrl: string): void {
    this.utilityService.downloadFile(fileUrl).subscribe((blob: Blob) => {
      // Use 'saveAs' from the FileSaver library to save the file
      saveAs(blob, fileUrl); // The file will be saved with the name passed as 'fileUrl'
    });
  } // Download the selected file
  // Args: fileUrl: string - The URL of the file to download
  // Returns: void

  deleteBackup(fileUrl: string): void {
    this.utilityService.deleteBackup(fileUrl).subscribe({
      next: (response) => {
        // Optionally, notify the user with a success message (e.g., Toast, alert)
        this.utilityService.getFiles().subscribe((response: string[]) => {
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
  } // Check the user's authentication level
  // Args: None
  // Returns: boolean

  confirmPopup(value: string, warning: boolean, event: any, fileURL: string) {
    const ConfirmationPopUp = this.dialog.open(ConfirmationPopupComponent);
    ConfirmationPopUp.afterOpened().subscribe(() => {
      ConfirmationPopUp.componentInstance.updatePopup(value, warning);
    });

    ConfirmationPopUp.afterClosed().subscribe((result: boolean) => {
      if (result === true && value === 'backupData') {
        console.log('Backup data');
        this.backupData(event);
      } else if (result === true && value === 'uploadData') {
        this.uploadFile();
      } else if (result === true && value === 'appendData') {
        this.appendFile();
      } else if (result === true && value === 'downloadData') {
        this.downloadFile(fileURL);
      } else if (result === true && value === 'loadData') {
        this.loadData(event);
      } else if (result === true && value === 'deleteBackup') {
        this.deleteBackup(fileURL);
      }
    });
  } // Confirm the action in the popup
  // Args: value: string - The action to confirm, warning: boolean - Whether it's a warning,
  // Args: event: any - The event that triggered the action, fileURL: string - The URL of the file to download
  // Returns: void
}
