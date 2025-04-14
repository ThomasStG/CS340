import { Component } from '@angular/core';
import { ItemData } from '../item-data';
import { Input } from '@angular/core';
import { UpdateItemService } from '../services/update-item.service';
import { MatDialogRef } from '@angular/material/dialog';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmationPopupComponent } from '../confirmation-popup/confirmation-popup.component';
import { UtilityService } from '../services/utility.service';
import { BehaviorSubject } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-admin-popup',
  templateUrl: './admin-popup.component.html',
  styleUrl: './admin-popup.component.css',
})
export class AdminPopupComponent {
  @Input() item: ItemData = {
    id: 0,
    name: '',
    size: '',
    is_metric: 'True',
    location: '',
    count: 0,
    threshold: 0,
  };
  itemTitle = '';

  isAdding = false;
  isEditing = false;
  value = 'none';
  darkMode = new BehaviorSubject<boolean>(false);

  constructor(
    public dialog: MatDialog,
    private updateItemService: UpdateItemService,
    private dialogRef: MatDialogRef<AdminPopupComponent>,
    private utilityService: UtilityService,
    private authService: AuthService
  ) {}
  newItem: ItemData = { ...this.item };
  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode());
    this.item.location = JSON.parse(this.item.location);
    this.newItem = this.item;
    if (this.item.name == '') {
      this.itemTitle = 'New Item';
      this.isAdding = true;
    } else {
      this.itemTitle = this.item.name;
    }
  }

  stopClickPropagation(event: Event) {
    event.stopPropagation();
  }

  editItem(event: Event) {
    event.stopPropagation();
    this.isEditing = true;
  }
  cancelEditing(event: Event) {
    event.stopPropagation();
    this.isEditing = false;
  }

  closePopup(event: Event) {
    event.stopPropagation();
    this.dialogRef.close();
    this.isEditing = false;
  }

  close() {
    this.dialogRef.close();
    this.isEditing = false;
    this.isAdding = false;
  }
  updateItem() {
    this.isEditing = false;
    this.close();
    this.updateItemService
      .updateItem(this.item, this.newItem)
      .subscribe((response) => {});
    // TODO: Close popup
    this.close();
  }
  deleteItem() {
    this.updateItemService.deleteItem(this.item).subscribe((response) => {});
    this.close();
  }
  addItem() {
    this.updateItemService.addItem(this.item);
    this.close();
  }

  cancelAdding(event: Event) {
    this.isAdding = false;
    // TODO: Close popup
  }

  showAddItemPopup() {
    this.isEditing = true;
    this.isAdding = true;
  }

  showItem(item: ItemData) {
    this.item = item;
  }

  confirmPopup(value: string) {
    const ConfirmationPopUp = this.dialog.open(ConfirmationPopupComponent);
    ConfirmationPopUp.afterOpened().subscribe(() => {
      ConfirmationPopUp.componentInstance.updatePopup(value);
    });

    ConfirmationPopUp.afterClosed().subscribe((result: boolean) => {
      if (result === true && value === 'save') {
        this.updateItem();
      }
      if (result === true && value === 'delete') {
        this.deleteItem();
      }
      if (result === true && value === 'add') {
        this.addItem();
      }
    });
  }
  check_level(){
    const level = this.authService.levelGetter().subscribe((level)=> {
    if (level < 2 ) return true
    else return false}
  )}
}
