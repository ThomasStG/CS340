import { Component, Inject } from '@angular/core';
import { AdminPopupComponent } from '../admin-popup/admin-popup.component';
import { MatDialogRef } from '@angular/material/dialog';
import { MatDialog } from '@angular/material/dialog';

@Component({
  selector: 'app-confirmation-popup',
  templateUrl: './confirmation-popup.component.html',
  styleUrl: './confirmation-popup.component.css'
})
export class ConfirmationPopupComponent {
  addItemMethod!: Function;
  deleteItemMethod!: Function;
  updateItemMethod!: Function;

  constructor(
    public dialog: MatDialog,
    private dialogRef: MatDialogRef<ConfirmationPopupComponent>,
  ){}

  isAdding = true;
  isEditing = false;

  confirm(event: Event){
    this.dialogRef.close(true);
  }

  cancel(event:Event){
    this.dialogRef.close(false);
  }

  updatePopup(value: string) {
    if(value == 'add'){
      this.isAdding = true;
      this.isEditing = false;
    }
    if(value == 'save'){
      this.isAdding = false;
      this.isEditing = true;
    }
    if(value == 'delete'){
      this.isAdding = false;
      this.isAdding = false;
    }  // Set the current action ('add', 'delete', 'update')
  }
}
