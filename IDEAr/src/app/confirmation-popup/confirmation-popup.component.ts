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
  action = ''
  warning = false;

  constructor(
    public dialog: MatDialog,
    private dialogRef: MatDialogRef<ConfirmationPopupComponent>,
    private utilityService: UtilityService,
  ) {}

  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode());
  }

  confirm(event: Event) {
    this.dialogRef.close(true);
  }

  cancel(event: Event) {
    this.dialogRef.close(false);
  }

  updatePopup(value: string, warning: boolean) {
    this.action = value;
    this.warning = warning;

    if(value === 'updateItem'){
      this.message = 'You are about to overwrite this item\'s data with new item data.';
    }
    if(value === 'deleteItem'){
      this.message = 'You are about to delete this item from the database.';
    }
    if(value === 'addItem'){
      this.message = 'You are about to add an item to the database.';
    }
    if(value === 'updateUser'){
      this.message = 'You are about to change this users information.';
    }
    if(value === 'deleteUser'){
      this.message = 'You are about to delete this user from the database.';
    }
    if(value === 'addUser'){
      this.message = 'You are about to add this user to the database.';
    }
    if(value === 'backupData'){
      this.message = 'You are about to create a backup of the database.';
    }
    if(value === 'uploadData'){
      this.message = 'You are about to upload a new file to the program (not to the database).';
    }
    if(value === 'appendData'){
      this.message = 'You are about to append the data to the database adding new data and updating current.';
    }
    if(value === 'downloadData'){
      this.message = 'You are about to create a downloaded .csv of the database.';
    }
    if(value === 'loadData'){
      this.message = 'You are about to load a .csv to the database and overwrite all data currently in the database.';
    }
  }

  loadDataPopup(){
    this.action = 'loadData';
  }
}
