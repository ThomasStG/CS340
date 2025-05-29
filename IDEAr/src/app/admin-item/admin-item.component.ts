import { Component, Input, OnInit } from '@angular/core';
import { ItemData } from '../item-data';
import { UpdateItemService } from '../services/update-item.service';
import { MatDialog } from '@angular/material/dialog';
import { AuthService } from '../services/auth.service';
import { AdminPopupComponent } from '../admin-popup/admin-popup.component';

@Component({
  selector: 'app-admin-item',
  templateUrl: './admin-item.component.html',
  styleUrl: './admin-item.component.css',
})
export class AdminItemComponent implements OnInit {
  constructor(
    private updateItemService: UpdateItemService,
    private authService: AuthService,
    private dialog: MatDialog,
  ) {}
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
  newItem: ItemData = { ...this.item };
  toChange = 0;
  ngOnInit() {
    /*
     * Sets the variable newItem to the value of item which is an empty variable.
     *
     * Args:
     *   None
     *
     * Returns:
     *   None
     */
    //this.item.location = JSON.parse(this.item.location);
    this.newItem = this.item;
  }

  isPopupVisible = false;
  isEditing = false;

  editItem(event: Event) {
    /*
     * Changes the variable editing to true for editing items
     *
     * Args:
     *   event: the event object
     *
     * Returns:
     *   None
     */
    event.stopPropagation();
    this.isEditing = true;
  }

  showPopup(event: any) {
    /*
     * Calls the admin popup component to display it as a dialog and opens it with the Item variable to be displayed
     *
     * Args:
     *   event: the event object
     *
     * Returns:
     *   None
     */
    this.dialog.open(AdminPopupComponent);
    const PopUp = this.dialog.open(AdminPopupComponent);
    PopUp.componentInstance.showItem(this.item);
  }

  closePopup(event: Event) {
    /*
     * changes the visibility variable and editing variable to false
     *
     * Args:
     *   event: the event object
     *
     * Returns:
     *   None
     */
    event.stopPropagation();
    this.isPopupVisible = false;
    this.isEditing = false;
  }
  updateItem(event: Event) {
    /*
     * Calls the updateItemService with the new item and current item to update the information
     *
     * Args:
     *   event: the event object
     *
     * Returns:
     *   None
     */
    event.stopPropagation();
    this.isEditing = false;
    this.isPopupVisible = false;
    this.updateItemService
      .updateItem(this.item, this.newItem)
      .subscribe((response) => {});
  }

  deleteItem(event: Event) {
    /*
     * Calls update item service with the time to delete
     *
     * Args:
     *   event: the event object
     *
     * Returns:
     *   None
     */
    event.stopPropagation();
    this.updateItemService.deleteItem(this.item).subscribe((response) => {});
  }

  incrementItem(event: Event) {
    /*
     * Calls update item service with current item and the value to increase count by
     *
     * Args:
     *   event: the event object
     *
     * Returns:
     *   None
     */
    event.stopPropagation();
    this.updateItemService
      .incrementItem(this.item, this.toChange)
      .subscribe((response) => {
        if (response.error) {
          console.error(response.error);
        } else {
          this.item.count += this.toChange;
        }
      });
  }

  decrementItem(event: Event) {
    /*
     * Calls update item service with current item and the value to derement count by
     *
     * Args:
     *   event: the event object
     *
     * Returns:
     *   None
     */
    event.stopPropagation();
    this.updateItemService
      .decrementItem(this.item, this.toChange)
      .subscribe((response) => {
        if (response.error) {
          console.error(response.error);
        } else {
          this.item.count -= this.toChange;
        }
      });
  }

}
