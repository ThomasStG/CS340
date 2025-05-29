import { Component, Inject, Input } from '@angular/core';
import { AdminPopupComponent } from '../admin-popup/admin-popup.component';
import { MatDialogRef } from '@angular/material/dialog';
import { MatDialog } from '@angular/material/dialog';
import { UtilityService } from '../services/utility.service';
import { BehaviorSubject } from 'rxjs';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-confirmation-popup',
  templateUrl: './confirmation-popup.component.html',
  styleUrl: './confirmation-popup.component.css',
  standalone: true,
  imports: [CommonModule],
})
export class ConfirmationPopupComponent {
  addItemMethod!: Function;
  deleteItemMethod!: Function;
  updateItemMethod!: Function;
  darkMode = new BehaviorSubject<boolean>(false);
  message = '';
  action = '';
  warning = false;

  constructor(
    public dialog: MatDialog,
    private dialogRef: MatDialogRef<ConfirmationPopupComponent>,
    private utilityService: UtilityService,
  ) {}

  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode());
  } // Initialize the component (confirmation popup)
  // Args: None
  // Returns: void

  confirm(event: Event) {
    this.dialogRef.close(true);
  } // Close the dialog  (confirm action)
  // Args: event: Event - The event that triggered the confirmation popup
  // Returns: void

  cancel(event: Event) {
    this.dialogRef.close(false);
  } // Close the dialog (cancel action)
  // Args: event: Event - The event that triggered the confirmation popup
  // Returns: void

  updatePopup(value: string, warning: boolean) {
    this.action = value;
    this.warning = warning;

    switch (value) {
      case 'updateItem':
        this.message =
          "You are about to overwrite this item's data with new item data.";
        break;

      case 'deleteItem':
        this.message = 'You are about to delete this item from the database.';
        break;

      case 'addItem':
        this.message = 'You are about to add an item to the database.';
        break;

      case 'updateUser':
        this.message = 'You are about to change this users information.';
        break;

      case 'deleteUser':
        this.message = 'You are about to delete this user from the database.';
        break;

      case 'addUser':
        this.message = 'You are about to add this user to the database.';
        break;

      case 'backupData':
        this.message = 'You are about to create a backup of the database.';
        break;

      case 'uploadData':
        this.message =
          'You are about to upload a new file to the program (not to the database).';
        break;

      case 'appendData':
        this.message =
          'You are about to append the data to the database adding new data and updating current.';
        break;

      case 'downloadData':
        this.message =
          'You are about to create a downloaded .csv of the database.';
        break;

      case 'loadData':
        this.message =
          'You are about to load a .csv to the database and overwrite all data currently in the database.';
        break;

      case 'missingData':
        this.message =
          'You are missing data for this action please go back and fill in the name, size, and metric to continue.';
        break;
      case 'deleteBackup':
        this.message = 'You are about to delete this backup file.';
        break;
      default:
        break;
    }
  } // Update the popup message and action based on the value and warning parameters
  // Args: value: string - The value to set the action to
  //       warning: boolean - The warning flag to set the warning message
  // Returns: void

  loadDataPopup() {
    this.action = 'loadData';
  } // Load data popup
  // Args: None
  // Returns: void
}
