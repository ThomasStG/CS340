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
    loc_shelf: '',
    loc_rack: '',
    loc_box: '',
    loc_row: '',
    loc_col: '',
    loc_depth: '',
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
    private authService: AuthService,
  ) {}
  newItem: ItemData = { ...this.item };
  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode()); // Check dark mode status
    this.newItem = this.item;
    if (this.item.name == '') {
      this.itemTitle = 'New Item';
      this.isAdding = true;
    } else {
      this.itemTitle = this.item.name;
    }
  } // Initialize the component (admin popup)
  // Args: None
  // Returns: void

  stopClickPropagation(event: Event) {
    event.stopPropagation();
  } // Prevent click event from propagating to the parent element
  // Args: event: Event
  // Returns: void

  editItem(event: Event) {
    event.stopPropagation();
    this.authService.getAuthLevel().subscribe((level) => {
      if (level < 2) {
        this.isEditing = true;
      }
    });
  } // Allow editing of the item through the popup
  // Args: event: Event
  // Returns: void
  cancelEditing(event: Event) {
    event.stopPropagation();
    this.isEditing = false;
  } // Cancel editing of the item through the popup
  // Args: event: Event
  // Returns: void

  closePopup(event: Event) {
    event.stopPropagation();
    this.dialogRef.close();
    this.isEditing = false;
  } // Close the popup when clicking outside of it
  // Args: event: Event
  // Returns: void

  close() {
    this.dialogRef.close();
    this.isEditing = false;
    this.isAdding = false;
  } // Close the popup when clicking outside of it
  // Args: None
  // Returns: void

  updateItem() {
    this.isEditing = false;
    this.close();
    this.updateItemService
      .updateItem(this.item, this.newItem)
      .subscribe((response) => {});

    this.close(); //close the popup
  } // update the item
  // Args: None
  // Returns: void

  deleteItem() {
    this.updateItemService.deleteItem(this.item).subscribe((then) => {
      this.close();
    });
  } // delete the item
  // Args: None
  // Returns: void

  addItem() {
    this.updateItemService.addItem(this.item).subscribe((then) => {
      this.close();
    });
  } // add the item
  // Args: None
  // Returns: void

  cancelAdding(event: Event) {
    this.isAdding = false;
    // cancel adding the item through the popup
  } // Args: event: Event
  // Returns: void

  showAddItemPopup() {
    this.isEditing = true;
    this.isAdding = true;
  } // show the add item popup
  // Args: None
  // Returns: void

  showItem(item: ItemData) {
    this.item = item;
  } // show the item in the popup
  // Args: item: ItemData
  // Returns: void

  confirmPopup(value: string, warning: boolean) {
    if (
      this.newItem['name'] === '' ||
      this.newItem['size'] === '' ||
      this.newItem['is_metric'] === ''
    ) {
      value = 'missingData';
      warning = true;
    } // Check if the item has all the required fields filled in

    const ConfirmationPopUp = this.dialog.open(ConfirmationPopupComponent);
    ConfirmationPopUp.afterOpened().subscribe(() => {
      ConfirmationPopUp.componentInstance.updatePopup(value, warning);
    }); // Open the confirmation popup and pass the value and warning to it

    ConfirmationPopUp.afterClosed().subscribe((result: boolean) => {
      if (result === true && value === 'updateItem') {
        this.updateItem();
      } // Update the item
      if (result === true && value === 'deleteItem') {
        this.deleteItem();
      } // Delete the item
      if (result === true && value === 'addItem') {
        this.addItem();
      } // Add the item
    });
  } // confirming popup actions
  // Args: value: string, warning: boolean
  // Returns: void

  check_level() {
    const level = this.authService.levelGetter().subscribe((level) => {
      if (level < 2) return true;
      else return false;
    });
  } // Check the level (access) of the user
  // Args: None
  // Returns: boolean
}
