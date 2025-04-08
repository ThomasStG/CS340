import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ItemData } from '../item-data';
import { UpdateItemService } from '../update-item.service';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-admin-popup',
  templateUrl: './admin-popup.component.html',
  styleUrl: './admin-popup.component.css',
})
export class AdminPopupComponent {
  item: ItemData = {
    id: 0,
    name: '',
    size: '',
    is_metric: 'True',
    location: '',
    count: 0,
    threshold: 0,
  };
  newItem: ItemData = { ...this.item };
  constructor(
    public dialog: MatDialog,
    private updateItemService: UpdateItemService,
    private authService: AuthService,
  ) {}

  isEditing = false;
  isAdding = false;
  editItem(event: Event) {
    event.stopPropagation();
    this.isEditing = true;
  }


  addingItem() {
    this.isEditing = true;
    this.isAdding = true;
  }

  showItem(item: Partial<ItemData>){
    if (item) {
      this.item = { ...this.item, ...item }; // Merge input data into the item
    }
    this.isEditing = false;
    this.isAdding = false;
  }

  updateItem(event: Event) {
    event.stopPropagation();
    this.isEditing = false;
    this.close();
    this.updateItemService
      .updateItem(this.item, this.newItem, this.authService.getToken())
      .subscribe((response) => {
        console.log(response);
      });
  }
  deleteItem(event: Event) {
    event.stopPropagation();
    this.updateItemService.deleteItem(this.item).subscribe((response) => {
      console.log(response);
    });
  }
  close() {
    this.isEditing = false;
    this.isAdding = false;
    this.dialog.closeAll();
  }
  save() {
    this.isEditing = false;
    this.isAdding = false;
    this.updateItemService.addItem(this.item).subscribe((response) => {
      if (response.error) {
        console.error(response.error);
      }
    });
    this.close();
  }
}
