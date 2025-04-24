import { Component } from '@angular/core';
import { Input, Output, EventEmitter } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { UtilityService } from '../services/utility.service';
import { BehaviorSubject } from 'rxjs';
import { ItemData } from '../item-data';

@Component({
  selector: 'app-item-popup',
  templateUrl: './item-popup.component.html',
  styleUrl: './item-popup.component.css',
})
export class ItemPopupComponent {
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
  }; // The item data to be displayed in the component
  // id
  // name
  // size
  // is_metric: whether the item is in metric or imperial units
  // loc_shelf: the shelf location of the item
  // loc_rack: the rack location of the item
  // loc_box: the box location of the item
  // loc_row: the row location of the item
  // loc_col: the column location of the item
  // loc_depth: the depth location of the item
  // count: the quantity of the item
  // threshold: the threshold quantity for the item

  darkMode = new BehaviorSubject<boolean>(false); 

  constructor(
    private dialogRef: MatDialogRef<ItemPopupComponent>,
    private utilityService: UtilityService,
  ) {}
  newItem: ItemData = { ...this.item };
  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode());
    console.log(this.item);
  } // Initialize the component (item popup)
  // Args: dialogRef: MatDialogRef<ItemPopupComponent> - Reference to the item popup dialog
  // Args: utilityService: UtilityService - Service for utility functions
  // Returns: void

  showItem(item: ItemData) {
    this.item = item;
  } // Show the item data in the popup
  // Args: item: ItemData - The item data to be displayed in the popup
  // Returns: void

  stopClickPropagation(event: Event) {
    event.stopPropagation();
  } // Stop click propagation to prevent closing the popup
  // Args: event: Event - The event that triggered the click
  // Returns: void

  closePopup(event: Event) {
    event.stopPropagation();
    this.dialogRef.close();
  } // Close the popup dialog
  // Args: event: Event - The event that triggered the close action
  // Returns: void

  @Output() close = new EventEmitter<void>(); // Emit an event when the popup is closed
  // Args: None
}
