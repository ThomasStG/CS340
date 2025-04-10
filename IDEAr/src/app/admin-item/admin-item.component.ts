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
    location: '',
    count: 0,
    threshold: 0,
  };
  newItem: ItemData = { ...this.item };
  toChange = 0;
  ngOnInit() {
    this.item.location = JSON.parse(this.item.location);
    this.newItem = this.item;
  }

  isPopupVisible = false;
  isEditing = false;

  editItem(event: Event) {
    event.stopPropagation();
    this.isEditing = true;
  }

  showPopup(event: any) {
    this.dialog.open(AdminPopupComponent);
    const PopUp = this.dialog.open(AdminPopupComponent);
    PopUp.componentInstance.showItem(this.item);
  }

  closePopup(event: Event) {
    event.stopPropagation();
    this.isPopupVisible = false;
    this.isEditing = false;
  }
  updateItem(event: Event) {
    event.stopPropagation();
    this.isEditing = false;
    this.isPopupVisible = false;
    this.updateItemService
      .updateItem(this.item, this.newItem)
      .subscribe((response) => {});
  }
  deleteItem(event: Event) {
    event.stopPropagation();
    this.updateItemService.deleteItem(this.item).subscribe((response) => {});
  }
  incrementItem(event: Event) {
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
