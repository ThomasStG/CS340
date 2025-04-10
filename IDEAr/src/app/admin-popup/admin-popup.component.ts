import { Component } from '@angular/core';
import { ItemData } from '../item-data';
import { Input } from '@angular/core';
import { UpdateItemService } from '../services/update-item.service';
import { MatDialogRef } from '@angular/material/dialog';

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
  isPopupVisible = false;
  isEditing = false;

  constructor(
    private updateItemService: UpdateItemService,
    private dialogRef: MatDialogRef<AdminPopupComponent>,
  ) {}
  newItem: ItemData = { ...this.item };
  ngOnInit() {
    this.item.location = JSON.parse(this.item.location);
    this.newItem = this.item;
    if (this.item.name == '') {
      this.itemTitle = 'New Item';
      this.isAdding = true;
    } else {
      this.itemTitle = this.item.name;
    }
  }

  editItem(event: Event) {
    event.stopPropagation();
    this.isEditing = true;
  }
  cancelEditing(event: Event) {
    event.stopPropagation();
    this.isEditing = false;
  }

  showPopup() {
    this.isPopupVisible = true;
  }

  closePopup(event: Event) {
    event.stopPropagation();
    this.isPopupVisible = false;
    this.isEditing = false;
  }
  updateItem(event: Event) {
    event.stopPropagation();
    this.isEditing = false;
    this.updateItemService
      .updateItem(this.item, this.newItem)
      .subscribe((response) => {});
    // TODO: Close popup
  }
  deleteItem(event: Event) {
    event.stopPropagation();
    this.updateItemService.deleteItem(this.item).subscribe((response) => {});
  }
  addItem(event: Event) {
    event.stopPropagation();
    this.updateItemService.addItem(this.item);
  }
  cancelAdding(event: Event) {
    this.isAdding = false;
    // TODO: Close popup
  }
  close() {
    this.dialogRef.close();
  }
  showItem(item: ItemData) {}
}
